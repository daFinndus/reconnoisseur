#!/usr/bin/env bash

# This script handles system checks and dependencies
# ---------------------------------------------------------------------

MANAGER=""

# Detect which supported package manager is available on the host
check_pkg_manager() {
	local apt_path=""
	local yay_path=""

	step "Checking for package manager..."
	info "Currently only apt and yay are supported!"

	apt_path=$(command -v apt)
	yay_path=$(command -v yay)

	if [[ -n "$apt_path" ]]; then
		MANAGER="apt"
	elif [[ -n "$yay_path" ]]; then
		MANAGER="yay"
	else
		error "No supported package manager found."
		exit 1
	fi

	success "Identified $MANAGER as the package manager."
}

# Verify required tools are installed and offer to install missing ones
check_pkgs() {
	local -a pkgs=("nmap" "ffuf" "ipcalc")
	local answer=""

	step "Checking for required packages..."

	for pkg in "${pkgs[@]}"; do
		if ! command -v "$pkg" &>/dev/null; then
			warn "Package $pkg is not installed. Installing..."

			if [[ "$YES" != "true" ]]; then
				# Ask before attempting to install a missing dependency
				read -r -p "[$(timestamp)] Do you want to install $pkg? (y/n) " answer

				if [[ "$answer" != "y" ]]; then
					error "Package $pkg is required. Exiting."
					exit 1
				fi
			else
				warn "Skipping confirmation prompt, installing $pkg!"
			fi

			# Install with the detected package manager
			case $MANAGER in
			apt)
				sudo apt update &>/dev/null && sudo apt install -y "$pkg" &>/dev/null
				;;
			yay)
				echo "y" | yay -S "$pkg" &>/dev/null
				;;
			esac

			if ! command -v "$pkg" &>/dev/null; then
				error "Failed to install $pkg. Please install it manually and re-run the script."
				exit 1
			fi

			success "Package $pkg installed successfully."
		else
			success "Package $pkg is installed."
		fi
	done

	info "Successfully installed all dependencies."
}
