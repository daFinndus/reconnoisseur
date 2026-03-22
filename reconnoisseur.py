#!/usr/bin/env python3

from __future__ import annotations

import sys

from modules.config import SETTINGS
from modules.finish import summarize
from modules.helpers import error, step
from modules.init import check_colors, init_workspace
from modules.nmap import Nmap
from modules.parser import parse_args
from modules.system import check_pkg_manager, check_pkgs
from modules.target import validate_target
from modules.web_enumeration import probe_web_services


# Run the full recon workflow from parsed CLI arguments.
def main(argv: list[str]) -> int:
    parse_args(argv, SETTINGS)

    step("Welcome to Reconnoisseur - Your automated recon toolkit.")

    # Check for colors (or not).
    if SETTINGS.color_check:
        check_colors(SETTINGS)

    # Retrieve the package manager and check for required packages.
    check_pkg_manager(SETTINGS)
    check_pkgs(SETTINGS)

    # Check if the provided target is usable.
    validate_target(SETTINGS)

    # Create a workspace (if file saving is enabled).
    if SETTINGS.save:
        init_workspace(SETTINGS)

    # Create the Nmap instance and run the port scan.
    nmap = Nmap(SETTINGS)

    if not nmap.portscan():
        error("Port scanning failed, exiting.")
        return 1

    # Scan for web services and add them to the hosts file if needed.
    web_results = probe_web_services(SETTINGS, nmap.ports)

    # TODO: Integrate ffuf pipeline
    # TODO: Add result parsing and reporting
    # TODO: Add CLI flags for web enum control
    # TODO: Add error handling and prerequisites
    # TODO: Add tests and sample fixtures

    # Print all results in a nice format here, save them if enabled.
    summarize(nmap.ports, web_results)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print("\n")
        error("Interrupted by user, exiting.")
        raise SystemExit(1)
