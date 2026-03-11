#!/usr/bin/env bash

# This script provides shared logging helpers
# -------------------------------------------

# Set up colors for readable log output
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
RESET="\033[0m"

# Return the current time for log message prefixes
timestamp() {
  date "+%H:%M:%S"
}

# Print a primary step message and pause briefly for readability
step() {
  echo -e "\n${CYAN}[$(timestamp)] ${RESET}$1"
  
  if [[ "$DELAY" == "true" ]]; then
    sleep 1s
  fi
}

# Print an informational log message
info() {
  echo -e "${BLUE}[$(timestamp)] ${RESET}$1"

  if [[ "$DELAY" == "true" ]]; then
    sleep 0.5s
  fi
}

# Print a success log message
success() {
  echo -e "${GREEN}[$(timestamp)] ${RESET}$1"
  
  if [[ "$DELAY" == "true" ]]; then
    sleep 0.5s
  fi
}

# Print a warning log message
warn() {
  echo -e "${YELLOW}[$(timestamp)] ${RESET}$1"
  
  if [[ "$DELAY" == "true" ]]; then
    sleep 0.5s
  fi
}

# Print an error log message and pause so it stays visible
error() {
  echo -e "${RED}[$(timestamp)] ${RESET}$1"
  
  if [[ "$DELAY" == "true" ]]; then
    sleep 1.5s
  fi
}