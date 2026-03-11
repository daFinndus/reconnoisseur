#!/usr/bin/env bash

# This script prepares the workspace directories
# -----------------------------------------------

source modules/helpers.sh
source modules/parser.sh

# Show a quick color preview for the current terminal
check_colors() {
  if [[ "$COLOR_CHECK" = "true" ]]; then
    warn "Skipping color support check as requested, this will save some time but might lead to suboptimal output formatting."
    return
  fi

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
  local name=""

  step "Creating necessary directories..."

  # Create the shared output directory if needed
  mkdir -p "output"
  success "Made sure that the output directory exists."

  # Create the shared wordlist directory if needed
  mkdir -p "wordlists"
  success "Also made sure that the wordlists directory exists."

  read -rp "[$(timestamp)] Please give this project a name: " name

  info "Using $name as the project name and creating workspace directories..."

  WORKSPACE="output/$name"

  # Reuse an existing workspace or create a new one for this run
  if [[ -d "$WORKSPACE" ]]; then
    warn "A workspace with the name $name already exists, using it..."
    sleep 1.5s

    warn "This will probably overwrite existing files, make sure nothing important is there!"
    sleep 1.5s

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
