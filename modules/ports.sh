#!/usr/bin/env bash

# This script handles port scanning
# --------------------------------

# This will replace slashes, colons, whitespaces and any other dangerous chars
sanitize_scan_name() {
  local value="$1"

  value="${value//\//_ }"
  value="${value//:/_}"
  value="${value// /_}"
  value="${value//[^[:alnum:]._-]/_}"

  printf '%s' "$value"
}

# Scan the target for open ports and save the results
portscan() {
  local output_name=""

  step "Proceeding with the port scan!"

  output_name=$(sanitize_scan_name "$TARGET")
  info "Using $output_name as the output name for $TARGET."

  # Create a dedicated directory for nmap output
  mkdir -p "$WORKSPACE/nmap"

  success "Created the nmap directory in the workspace!"

  info "Doing an nmap scan on $TARGET now..."

  # Set the output directory
  local output_directory="$WORKSPACE/nmap/$output_name"

  if [[ "$SUBNET" == "true" ]]; then
    info "Subnet mode is enabled, so the scan will discover live hosts and then scan each of them."
    scan_subnet_hosts "$output_directory" || return 1
  else
    scan_host_ports "$output_directory" "$TARGET" || return 1
  fi

  success "Port scanning finished. Results are stored in $WORKSPACE/nmap."
}

# This function will scan the target for open ports and save the results, then proceed to run a service scan
scan_host_ports() {
    local output="$1"
    local host="$2"

    local ports=""
    local scan_confirm=""

    if [[ "$YES" != "true" ]]; then
        read -rp "[$(timestamp)] Do you wanna run a nmap scan on $host? (y/n) " scan_confirm

        if [[ "$scan_confirm" != "y" ]]; then
            info "Skipping $host as requested."
            return 0
        fi
    else
        warn "Skipping confirmation prompt again, scanning $host!"
    fi

    if [[ "$FULL_PORT_SCAN" == "true" ]]; then
        info "Scanning all TCP ports on $host. This may take a while."

        if ! run_nmap_scan "$output" -Pn -p- "$host"; then
            error "Port scan failed for $host."
            return 1
        fi
    else
        info "Scanning nmap's default top 1000 TCP ports on $host."

        if ! run_nmap_scan "$output" -Pn "$host"; then
            error "Port scan failed for $host."
            return 1
        fi
    fi

    ports=$(extract_ports "$output.gnmap")

    # Add a newline before the ports output for better formatting
    printf '\n'

    if [[ -n "$ports" ]]; then
        success "Open TCP ports on $host: $ports"
    else
        warn "No open TCP ports found on $host."
    fi

    run_service_scan  "$output" "$host" "$ports" || return 1

}

# This will run a service scan on the specified host and open ports
run_service_scan() {
    local output="$1"
    local host="$2"
    local ports="$3"

    if [[ "$SERVICE_SCAN" != "true" ]]; then
        info "Skipping service detection for $host because it was disabled via CLI option."
        return 0
    fi

    if [[ -z "$ports" ]]; then
        warn "Skipping service detection for $host because no open TCP ports were found."
        return 0
    fi

    info "Running service detection against $host on ports $ports."

    if ! run_nmap_scan "$output"-service -Pn -sV -sC -p "$ports" "$host"; then
        error "Service detection failed for $host."
        return 1
    fi

    # Add a newline for better formatting
    printf '\n'

    success "Saved service detection results to $output-service.nmap, .gnmap and .xml."
}

scan_subnet_hosts() {
    local output="$1"

    local hosts_file="$WORKSPACE/nmap/hosts.log"
    local -a hosts=()
    local host=""

    info "Discovering live hosts inside $TARGET first."

    if ! run_nmap_scan "$output" -sn "$TARGET"; then
        error "Host discovery failed for $TARGET."
        return 1
    fi

    mapfile -t hosts < <(extract_live_hosts "$output.gnmap")

    if [[ "${#hosts[@]}" -eq 0 ]]; then
        warn "No live hosts were discovered in $TARGET."
        return 0
    fi

    printf '%s\n' "${hosts[@]}" > "$hosts_file"

    # Add a newline for better formatting
    printf '\n'

    success "Discovered ${#hosts[@]} live host(s). Saved the list to $hosts_file."

    for host in "${hosts[@]}"; do
        # Grep the last octet of the host
        local octet="${host##*.}"

        step "Scanning discovered host $host"
        scan_host_ports "$output-$octet" "$host" || return 1
    done
}

# This function is for running the nmap scan
run_nmap_scan() {
  # Where to put the nmap scan results
  local output="$1"

  shift

  # cmd is an array of commands, that's the -a flag
  local -a cmd=(nmap)

  [ "$VERBOSE" == "true" ] && cmd+=(-v)

  cmd+=("$@" -oA "$output")

  info "Running: ${cmd[*]}"

  "${cmd[@]}"
}

# This will extract all open ports, then return them as a comma-separated list
extract_ports() {
  local gnmap_file="$1"

  awk -F'Ports: ' '
    /Ports: / {
      n = split($2, entries, ", ")
      for (i = 1; i <= n; i++) {
        split(entries[i], fields, "/")
        if (fields[2] == "open") {
          print fields[1]
        }
      }
    }
  ' "$gnmap_file" | sort -n -u | paste -sd, -
}

# This function will grab all running hosts
extract_live_hosts() {
  local gnmap_file="$1"

  awk '/Status: Up/ { print $2 }' "$gnmap_file"
}