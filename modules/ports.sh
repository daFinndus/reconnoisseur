#!/usr/bin/env bash

# This script handles port scanning
# --------------------------------

source modules/helpers.sh
source modules/init.sh
source modules/parser.sh

# Scan the target for open ports and save the results
portscan() {
    local answer=""

    step "Proceeding with the port scan!"

    info "Doing an nmap scan on $TARGET now...\n"

    # Create a dedicated directory for nmap output
    mkdir -p "$WORKSPACE/nmap"

    success "Created the nmap directory in the workspace!"

    info "Only checking open ports first."

    # Let the user choose between a full scan and the default top ports
    read -rp "[$(timestamp)] By default only port 1-1024 is checked, do you wanna scan all? (y/n) " answer

    if [ "$answer" == "y" ]; then
        info "Scanning all available ports, this might take a while. Go drink something."
        nmap "$TARGET" -p- -Pn -oA "$WORKSPACE/nmap/$TARGET" &> /dev/null
    else
        info "Scanning until port 1024, this shouldn't take too long."
        nmap "$TARGET" -Pn -oA "$WORKSPACE/nmap/$TARGET" &> /dev/null
    fi

    success "Scan's done, saving results to $WORKSPACE/nmap/$TARGET.nmap, .gnmap and .xml!"
}