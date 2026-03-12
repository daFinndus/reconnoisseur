#!/usr/bin/env bash

# This script prepares the workspace directories
# -----------------------------------------------

# Show a quick color preview for the current terminal
check_colors() {
  [ "$COLOR_CHECK" == "false" ] && return

  step "Checking if the terminal displays colors correctly..."

  info "This should be blue."
  success "This should be green."
  warn "This should be yellowish."
  error "This should be red."

  info "The script can run without the colors being a 100% match."
}

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

  if [[ -n "$PROJECT_NAME" ]]; then
    info "Project name provided via CLI, creating workspace..."
  else
    read -rp "[$(timestamp)] Please give this project a name: " name

    info "Using $name as the project name and creating workspace directories..."
  fi

  WORKSPACE="${OUTPUT:-$DEFAULT_OUTPUT}/${PROJECT_NAME:-$name}"

  # Reuse an existing workspace or create a new one for this run
  if [[ -d "$WORKSPACE" ]]; then
    warn "A workspace with the name ${PROJECT_NAME:-$name} already exists, using it..."
    warn "This will probably overwrite existing files, make sure nothing important is there!"

    if [[ "$YES" == "false" ]]; then
      read -rp "[$(timestamp)] Do you want to continue with this workspace? (y/n) " answer

      if [[ "$answer" != "y" ]]; then
        error "Probably a good decision, good bye!"
        exit 1
      fi
    else
      warn "Skipping confirmation prompt as requested, be careful with that!"
    fi
  fi
  
  mkdir -p "$WORKSPACE"
  success "Workspace created!"

  info "The output directory for this project lies in $WORKSPACE."
}
