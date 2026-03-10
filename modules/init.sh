#!/usr/bin/env bash

# This script prepares the workspace directories
# -----------------------------------------------

source modules/helpers.sh
source modules/parser.sh

# Exit unless the script runs with root privileges
make_sure_root() {
  if [ "$EUID" -ne 0 ]; then
    error "Please run as root!"
    info "Port scanning and enumeration requires elevated privileges."

    sleep 3s
    exit 1
  fi
}

# Show a quick color preview for the current terminal
check_colors() {
  step "Checking if the terminal displays colors correctly..."

  info "This should be blue."
  success "This should be green."
  warn "This should be yellowish."
  error "This should be red."

  info "The script can run without the colors being a 100% match."
}

WORKSPACE=""

# Ensure the output and wordlist directories exist
init_workspace() {
  local project_name=""

  step "Creating necessary directories..."

  if [ -z "$OUTPUT" ]; then
    OUTPUT="output"
  fi

  # Create the shared output directory if needed
  mkdir -p "$OUTPUT"

  success "Made sure that the output directory exists."

  if [ -z "$WORDLISTS" ]; then
    WORDLISTS="wordlists"
  fi

  # Create the shared wordlist directory if needed
  mkdir -p "$WORDLISTS"

  read -rp "[$(timestamp)] Please give this project a name: " project_name

  info "Using $project_name as the project name and creating workspace directories..."

  WORKSPACE="$OUTPUT/$project_name"

  # Reuse an existing workspace or create a new one for this run
  if [ -d "$WORKSPACE" ]; then
    warn "A workspace with the name $project_name already exists, using it..."
    sleep 1.5s
    warn "This will probably overwrite existing files, make sure nothing important is there!"
    sleep 3s

    read -rp "[$(timestamp)] Do you want to continue with this workspace? (y/n) " answer

    if [[ "$answer" != "y" ]]; then
      error "Probably a good decision, good bye!"
      exit 1
    fi
  else
    mkdir -p "$WORKSPACE"
    success "Workspace created at $WORKSPACE."
  fi

  info "The output directory for this project lies in $WORKSPACE, you can find all results there."
  success "Also checked the wordlists directory!"
}
