#!/usr/bin/env python3

from __future__ import annotations

import sys

from modules.config import SETTINGS
from modules.helpers import step, error
from modules.init import check_colors, init_workspace
from modules.nmap import portscan
from modules.web_enumeration import extract_webserver
from modules.system import check_pkg_manager, check_pkgs
from modules.parser import (
    parse_args,
    validate_output,
    validate_pingout,
    validate_project_name,
    validate_target,
)


# Run the full recon workflow from parsed CLI arguments.
def main(argv: list[str]) -> int:
    try: 
        parse_args(argv, SETTINGS)

        step("Welcome to Reconnoisseur - Your automated recon toolkit.\n")

        validate_pingout(SETTINGS)
        validate_output(SETTINGS)
        validate_project_name(SETTINGS)

        check_colors(SETTINGS)
        check_pkg_manager(SETTINGS)
        check_pkgs(SETTINGS)

        validate_target(SETTINGS)
        init_workspace(SETTINGS)


        if not portscan(SETTINGS):
            return 1
        
        extract_webserver(SETTINGS)

        # TODO: Add Nmap XML parsing for web hints
        # TODO: Build target URL candidates
        # TODO: Implement web reachability check
        # TODO: Detect hostname redirects
        # TODO: Add safe hosts-file workflow
        # TODO: Integrate ffuf pipeline
        # TODO: Add result parsing and reporting
        # TODO: Add CLI flags for web enum control
        # TODO: Add error handling and prerequisites
        # TODO: Add tests and sample fixtures
    except KeyboardInterrupt:
        print("\n")
        error("Interrupted by user, exiting...")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
