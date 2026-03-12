#!/usr/bin/env bash

# This script parses and validates CLI arguments
# --------------------------------------------------

# Print CLI usage information
print_help() {
	echo "Reconnoisseur v1.0.0 (https://github.com/daFinndus/reconnoisseur)"

	echo -e "\nUsage: $0 [options]"

	echo -e "\nOptions:"
	echo -e "\t-t, --target\t\tTarget domain or IP address."
	echo -e "\t-pt, --pingout\t\tTimeout for host reachability check in seconds (default: 10)."
	echo -e "\t-fp, --full-ports\tScan all 65535 TCP ports instead of the default top 1000."
	echo -e "\t-nss, --no-service-scan\tSkip the follow-up service detection scan."
	echo -e "\t-y, --yes\t\tSkip all confirmation prompts, use with caution!"
	echo
	echo -e "\t-o, --output\t\tSpecify a custom output directory for all results."
	echo
	echo -e "\t-ncc, --no-color-check\tDisable color support check, save some time."
	echo -e "\t-pn, --project-name\tSpecify the project name, skip whole init section."
	echo -e "\t-v, --verbose\t\tEnable verbose logging."
	echo -e "\t-nd, --no-delay\t\tDisable the delay after chat messages."
	echo -e "\nExample: $0 -t 10.10.0.10 -pt 15 -v"
}

# Exit early when the user only asks for help
check_help() {
	if [[ "$1" == "-h" || "$1" == "--help" ]]; then
		print_help
		exit 0
	fi
}

# Parse command-line arguments into global variables
parse_args() {
	while [[ "$#" -gt 0 ]]; do
		case $1 in
		-t | --target)
			require_value "$1" "${2-}"
			TARGET="$2"
			shift
			;;
		-pt | --pingout)
			require_value "$1" "${2-}"
			PINGOUT="$2"
			shift
			;;
		-fp | --full-ports)
			FULL_PORT_SCAN=true
			;;
		-nss | --no-service-scan)
			SERVICE_SCAN=false
			;;
		-y | --yes)
			YES=true
			;;
		-o | --output)
			require_value "$1" "${2-}"
			OUTPUT="$2"
			shift
			;;
		-ncc | --no-color-check)
			COLOR_CHECK=false
			;;
		-pn | --project-name)
			require_value "$1" "${2-}"
			PROJECT_NAME="$2"
			shift
			;;
		-v | --verbose)
			VERBOSE=true
			;;
		-nd | --no-delay)
			DELAY=false
			;;
		-h | --help)
			error "Help option detected, please run without additional arguments!"
			exit 1
			;;
		*)
			error "Unknown parameter passed: $1."
			exit 1
			;;
		esac
		shift
	done

	if [[ -z "$TARGET" ]]; then
		error "The target is required but was not provided. Specify via -t."
		exit 1
	fi
}

# Ensure options that require values are not missing their arguments
require_value() {
	local name="$1"
	local value="${2-}"

	if [[ -z "$value" ]]; then
		error "Option $name requires a value."
		exit 1
	fi
}

# Verify the target is reachable before recon begins
# Checks for single host or subnet, sanitizes the target, checks reachability
validate_target() {
	# This stores the specified subnet and local subnets of the host
	local subnet=""
	local -a local_subnets=()

	step "Validating the target now..."

	# Validate the target before any network checks run
	if [[ "$TARGET" =~ [[:space:]] ]]; then
		error "The target must not contain whitespace."
		exit 1
	elif contains_control_chars "$TARGET"; then
		error "The target contains unsupported control characters."
		exit 1
	elif ! is_valid_target "$TARGET"; then
		error "The target must be a valid IPv4 address, hostname, or IPv4 CIDR range."
		exit 1
	fi

	success "Target $TARGET looks good, let's see if it's reachable."

	step "Checking reachability of the target..."

	if [[ "$TARGET" == *"/"* ]]; then
		info "Seems you are using a subnet, checking compatibility..."

		IFS=' ' read -r -a local_subnets <<<"$(ip route | grep -F '/' | awk '{print $1}')"

		info "Found the following local subnets: ${local_subnets[*]}."

		# Compare the target network with the local network
		subnet=$(ipcalc -n "$TARGET" | awk '/Network/ {print $2}')

		if [[ " ${local_subnets[*]} " == *" $subnet "* ]]; then
			success "You are in the same subnet as the provided target, good job!"

			SUBNET=true
		else
			error "Please make sure you are in the same subnet as the target."
			info "The target subnet is $subnet and yours is $local_subnets. Gotta check up on that."

			exit 1
		fi
	else
		info "The target is a single host, checking if it's reachable."

		# Send a single ping request and check whether it succeeded
		if ping -c 1 -W "${PINGOUT:-$DEFAULT_PINGOUT}" "$TARGET" >/dev/null 2>&1; then
			success "The target $TARGET is reachable. Proceeding with recon."
		else
			error "The target $TARGET is not reachable. Please check the address and try again."
			exit 1
		fi
	fi
}

# Checks that the ping timeout is a positive integer
validate_pingout() {
	if [[ -z "$PINGOUT" ]]; then
		info "No ping timeout specified, using default value of 10 seconds."
	elif is_positive_integer "$PINGOUT"; then
		success "Updated ping timeout: $PINGOUT seconds."

		return
	else
		error "Please choose a positive number for the ping timeout!"
		info "Using default value of 10 seconds!"
	fi

	PINGOUT="$DEFAULT_PINGOUT"
}

# Validate output path before they reach filesystem commands
# Clears control chars
validate_output() {
	if [[ -z "$OUTPUT" ]]; then
		info "No output directory specified, using default value 'output'."

		OUTPUT="$DEFAULT_OUTPUT"
		return
	elif contains_control_chars "$OUTPUT"; then
		error "The output directory contains unsupported control characters."
		exit 1
	fi

	success "Updated output directory: $OUTPUT."
	info "Let's hope nothing breaks..."
}

# Basically the same check as the function above
# Could be merged but I want to keep them separate for better error messages and future flexibility
validate_project_name() {
	if [[ -z "$PROJECT_NAME" ]]; then
		info "No project name specified, will ask for it during workspace initialization."

		return
	elif contains_control_chars "$PROJECT_NAME"; then
		error "The project name contains unsupported control characters."
		exit 1
	fi

	success "Updated project name: $PROJECT_NAME."
	info "Let's hope nothing breaks..."
}
