#!/usr/bin/env bash

# This script provides shared logging helpers
# -------------------------------------------

# Set up colors for readable log output
readonly COLORS=(
  RED="\e[31m"
  GREEN="\e[32m"
  YELLOW="\e[33m"
  BLUE="\e[34m"
  CYAN="\e[36m"
  RESET="\e[0m"
)

# Return the current time for log message prefixes
timestamp() {
  date "+%H:%M:%S"
}

# Print a primary step message and pause briefly for readability
step() {
  echo -e "\n${COLORS[4]}[$(timestamp)] ${COLORS[-1]}$1"
  
  if [[ "$DELAY" == "true" ]]; then
    sleep 1s
  fi
}

# Print an informational log message
info() {
  echo -e "${COLORS[3]}[$(timestamp)] ${COLORS[-1]}$1"

  if [[ "$DELAY" == "true" ]]; then
    sleep 0.5s
  fi
}

# Print a success log message
success() {
  echo -e "${COLORS[2]}[$(timestamp)] ${COLORS[-1]}$1"
  
  if [[ "$DELAY" == "true" ]]; then
    sleep 0.5s
  fi
}

# Print a warning log message
warn() {
  echo -e "${COLORS[2]}[$(timestamp)] ${COLORS[-1]}$1"
  
  if [[ "$DELAY" == "true" ]]; then
    sleep 0.5s
  fi
}

# Print an error log message and pause so it stays visible
error() {
  echo -e "${COLORS[1]}[$(timestamp)] ${COLORS[-1]}$1"
  
  if [[ "$DELAY" == "true" ]]; then
    sleep 1.5s
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