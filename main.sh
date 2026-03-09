#!/usr/bin/env bash

# This file executes the main logic
# ---------------------------------

# Source all modules
source modules/helpers.sh
source modules/init.sh
source modules/parser.sh

# Parse arguments here - ip address or URL, maybe additional params
check_vars $@
validate_vars

# Create workspace directories and global variables
init_workspace

# Check for OS here or only for installed package manager

# Validate installed programs

# Run port scan, check open ports and services, save via -oA

# If webserver running, enumeration

# Directories, Sub-domains, VHosts, add everything to /etc/hosts

# Technology fuzzing here, check via HTTP headers and extension fuzzing

# File fuzzing, parameter fuzzing

# Check for forms, etc.

# Parse outputs into structured format, remove duplicates, correlate findings per host

# Generate final summary in markdown

# Remove temporary files, print final paths and stat
