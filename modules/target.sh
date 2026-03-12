#!/usr/bin/env bash

# This script holds target validation functions
# ---------------------------------------------

# Validate IPv4 addresses one octet at a time
is_valid_ipv4() {
	local candidate="$1"
	local octets=()

	[[ "$candidate" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || return 1

	# Split the candidate by dots into octets
	IFS='.' read -r -a octets <<<"$candidate"

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
