#!/usr/bin/env python3

from __future__ import annotations

import sys

from modules.config import SETTINGS
from modules.helpers import step
from modules.init import check_colors, init_workspace
from modules.ports import portscan
from modules.system import check_pkg_manager, check_pkgs
from modules.parser import (
    check_help,
    parse_args,
    validate_output,
    validate_pingout,
    validate_project_name,
    validate_target,
)


# Run the full recon workflow from parsed CLI arguments.
def main(argv: list[str]) -> int:
    check_help(argv)
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
