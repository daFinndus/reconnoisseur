#!/usr/bin/env bash

# This script runs the main recon workflow
# ---------------------------------

# Source all modules
source modules/config.sh
source modules/helpers.sh
source modules/init.sh
source modules/parser.sh
source modules/target.sh
source modules/system.sh
source modules/ports.sh

# Check for help before doing anything else
check_help "$1"

# Then parse the rest of the arguments
parse_args "$@"

# Show the welcome message
step "Welcome to Reconnoisseur - Your automated recon toolkit."

# Validate all args not depending on other packages
validate_pingout
validate_output
validate_project_name

# Check terminal colors
check_colors

# Detect the package manager
check_pkg_manager

# Validate required tools
check_pkgs

# Validate the target
validate_target

# Prepare the workspace
init_workspace

# Run the initial port scan
portscan

# If a web server is running, continue with web enumeration

# Enumerate directories, subdomains, and virtual hosts

# Detect technologies through headers and extension probing

# Fuzz files and parameters

# Check for forms and similar inputs

# Correlate results and remove duplicates

# Generate the final Markdown summary

# Clean up temporary files and print final paths
