#!/usr/bin/env bash

# This script parses and validates CLI arguments
# --------------------------------------------------

source modules/helpers.sh

# Print CLI usage information
print_help() {
  echo "Reconnoisseur v1.0.0 (https://github.com/daFinndus/reconnoisseur)"

  echo -e "\nUsage: $0 [options]"

  echo -e "\nOptions:"
  echo -e "\t-t, --target\tTarget domain or IP address."
  echo -e "\t-pt, --pingout\tTimeout for host reachability check in seconds (default: 10)."
  echo -e "\t-v, --verbose\tEnable verbose logging."
  echo -e "\t-o, --output\tOverwrite output directory, not recommended."
  echo -e "\t-w, --wordlists\tOverwrite wordlist directory, not recommended."

  echo -e "\nExample: $0 -t 10.10.0.10 -pt 15 -v"
}

# Exit early when the user only asks for help
check_help() {
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    print_help
    exit 0
  fi
}

TARGET=""
VERBOSE=false
OUTPUT=""
WORDLISTS=""

PINGOUT=""

# Ensure options that require values are not missing their arguments
require_value() {
  local name="$1"
  local value="${2-}"

  if [[ -z "$value" ]]; then
    error "Option $name requires a value."
    exit 1
  fi
}

# Return success when the provided value is a positive integer
is_positive_integer() {
  [[ "$1" =~ ^[1-9][0-9]*$ ]]
}

# Reject values that contain control characters
contains_control_chars() {
  [[ "$1" =~ [[:cntrl:]] ]]
}

# Parse command-line arguments into global variables
check_vars() {
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
    -o | --output)
      require_value "$1" "${2-}"
      OUTPUT="$2"
      shift
      ;;
    -w | --wordlists)
      require_value "$1" "${2-}"
      WORDLISTS="$2"
      shift
      ;;
    -v | --verbose)
      VERBOSE=true
      shift
      ;;
    *)
      error "Unknown parameter passed: $1."
      ;;
    esac
    shift
  done
}

# Validate IPv4 addresses one octet at a time
is_valid_ipv4() {
  local candidate="$1"
  local octets=()

  [[ "$candidate" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || return 1

  # Split the candidate by dots into octets
  IFS='.' read -r -a octets <<< "$candidate"

  # Make sure each octet is between 0 and 255
  for octet in "${octets[@]}"; do
    ((octet >= 0 && octet <= 255)) || return 1
  done
}

# Validate hostnames made of DNS-compatible labels
is_valid_hostname() {
  local candidate="$1"

  [[ ${#candidate} -le 253 ]] || return 1
  [[ "$candidate" =~ ^[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*$ ]] || return 1
}

# Accept IPv4 hosts, DNS names, and IPv4 CIDR ranges
is_valid_target() {
  local candidate="$1"
  local address=""
  local prefix=""

  if [[ "$candidate" == */* ]]; then
    address="${candidate%/*}"
    prefix="${candidate#*/}"

    info "Got address $address and prefix $prefix from the provided CIDR notation."

    is_valid_ipv4 "$address" || return 1

    # Check whether the prefix is a number between 0 and 32
    [[ "$prefix" =~ ^[0-9]+$ ]] || return 1
    ((prefix >= 0 && prefix <= 32)) || return 1

    return 0
  fi

  is_valid_ipv4 "$candidate" || is_valid_hostname "$candidate"
}

# Validate parsed CLI variables and log the chosen configuration
validate_vars() {
  step "Validating variables now..."

  # Validate the target before any network checks run
  if [ -z "$TARGET" ]; then
    error "The target wasn't provided!"
    exit 1
  elif [[ "$TARGET" =~ [[:space:]] ]]; then
    error "The target must not contain whitespace."
    exit 1
  elif contains_control_chars "$TARGET" || ! is_valid_target "$TARGET"; then
    error "The target must be a valid IPv4 address, hostname, or IPv4 CIDR range."
    exit 1
  else
    success "Updated target: $TARGET."
  fi

  # Use a sane timeout range for reachability checks
  if [ -z "$PINGOUT" ]; then
    info "No ping timeout provided, using default of 10 seconds."

    PINGOUT=10
  else
    if is_positive_integer "$PINGOUT" && ((PINGOUT > 0)) && ((PINGOUT <= 120)); then
      success "Updated ping timeout: $PINGOUT seconds."
    else
      warn "Invalid ping timeout (1-120), using default value of 10 seconds!"
      PINGOUT=10
    fi
  fi

  # Validate output and wordlist paths before they reach filesystem commands
  if [ -n "$OUTPUT" ]; then
    if contains_control_chars "$OUTPUT"; then
      error "The output directory contains unsupported control characters."
      exit 1
    fi

    success "Updated output directory: $OUTPUT."
    info "Let's hope nothing breaks..."
  else
    info "Gonna put the output right in this directory!"
  fi

  if [ -n "$WORDLISTS" ]; then
    if contains_control_chars "$WORDLISTS"; then
      error "The wordlists directory contains unsupported control characters."
      exit 1
    fi

    success "Updated wordlists directory: $WORDLISTS."
    info "All damage will be because of you!"
  else
    info "Using default values for the wordlists directory."
  fi

  # Show the selected logging level
  if [[ "$VERBOSE" == "true" ]]; then
    success "Logging is now verbose. Good luck with that!"
  else
    info "Logging will stay as silent as possible."
  fi

  success "Variable validation succeeded, nice job."
}

# Verify the target is reachable before recon begins
validate_target() {
  local interface=""
  local ip_address=""
  local subnet=""
  local local_subnet=""

  step "Checking reachability of the target..."

  interface=$(ip route | grep default | awk '{print $5}')
  ip_address=$(ip addr show "$interface" | grep 'inet ' | awk '{print $2}' | cut -d'/' -f1)

  if [[ "$TARGET" == *"/"* ]]; then
    info "Seems you are using a subnet, checking compatibility..."

    # Compare the target network with the local network
    subnet=$(ipcalc -n "$TARGET" | awk '/Network/ {print $2}')
    local_subnet=$(ipcalc -n "$ip_address" | awk '/Network/ {print $2}')

    if [[ "$local_subnet" == "$subnet" ]]; then
      success "You are in the same subnet as the provided target, good job!"
    else
      error "Please make sure you are in the same subnet as the target."
      info "The target subnet is $subnet and your subnet is $local_subnet. Gotta check up on that."
      exit 1
    fi
  else
    info "The target is a single host, checking if it's reachable."

    # Send a single ping request and check whether it succeeded
    if ! ping -c 1 -W "$PINGOUT" "$TARGET" | grep -q bytes; then
      error "The target $TARGET is not reachable. Please check the address and try again."
      exit 1
    else
      success "The target $TARGET is reachable. Proceeding with recon."
    fi
  fi
}
