#!/usr/bin/env bash

# Here are helper functions for logging, etc.
# -------------------------------------------

# Setup colors for nice logging
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
RESET="\033[0m"

timestamp() {
  date "+%H:%M:%S"
}

# Logging functions
step() {
  echo -e "\n${CYAN}[$(timestamp)] ${RESET} $1"
}

info() {
  echo -e "${BLUE}[$(timestamp)] ${RESET} $1"
}

success() {
  echo -e "${GREEN}[$(timestamp)] ${RESET} $1"
}

warn() {
  echo -e "${YELLOW}[$(timestamp)] ${RESET} $1"
}

error() {
  echo -e "${RED}[$(timestamp)] ${RESET} $1"
}
