#!/usr/bin/env bash

# This file is for creating necessary directories
# -----------------------------------------------

source modules/helpers.sh
source modules/parser.sh

init_workspace() {
  step "Creating necessary directories..."

  sleep 1s

  if [ -z "$OUTPUT" ]; then
    mkdir -p "$(pwd)/output"
  else
    mkdir -p "$OUTPUT"
  fi

  success "Made sure that the output directory exists.."

  sleep 1.5s

  if [ -z "$WORDLISTS" ]; then
    mkdir -p "$(pwd)/wordlists"
  else
    mkdir -p "$WORDLISTS"
  fi

  success "Also checked up on the wordlists directory!"

  sleep 1s
}
