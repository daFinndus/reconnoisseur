#!/usr/bin/env bash

# Here is the validation logic for the passed params
# --------------------------------------------------

source modules/helpers.sh

print_help() {
  echo "Reconnoisseur - Your automated recon toolkit"

  echo -e "\nOptions:"
  echo -e "\t-t, --target\tTarget domain or IP address"
  echo -e "\t-o, --output\tOverwrite output directory, not recommended"
  echo -e "\t-w, --wordlists\tOverwrite wordlist directory, not recommended"
  echo -e "\t-v, --verbose\tEnable verbose logging"
}

TARGET=""
VERBOSE=false
OUTPUT=""
WORDLISTS=""

check_vars() {
  while [[ "$#" -gt 0 ]]; do
    case $1 in
    -h | --help)
      print_help
      exit 1
      ;;
    -t | --target)
      TARGET="$2"
      shift
      ;;
    -o | --output)
      OUTPUT="$2"
      shift
      ;;
    -w | --wordlists)
      WORDLISTS="$2"
      shift
      ;;
    -v | --verbose)
      VERBOSE=true
      shift
      ;;
    *)
      error "Unknown parameter passed: $1"
      ;;
    esac
    shift
  done
}

validate_vars() {
  step "Validating variables now"

  if [ -z "$TARGET" ]; then
    error "The target wasn't provided"
    exit 1
  else
    success "Updated target: $TARGET"
    sleep 1.5s
  fi

  if [ -n "$OUTPUT" ]; then
    success "Updated output directory: $OUTPUT"
    sleep 1s
    info "Let's hope nothing breaks..."
    sleep 1.5s
  else
    info "Gonna put the output right in this directory!"
    sleep 1.5s
  fi

  if [ -n "$WORDLISTS" ]; then
    success "Updated wordlists directory: $WORDLISTS"
    sleep 1s
    info "All damage will be because of you!"
    sleep 1.5s
  else
    info "Using default values for the wordlists directory"
    sleep 1.5s
  fi

  if [ $VERBOSE="true" ]; then
    success "Logging is now verbose"
  else
    info "Logging will stay as silent as possible"
  fi

  sleep 1.5s

  info "Variable validation is complete, nice job"

  sleep 1.5s
}
