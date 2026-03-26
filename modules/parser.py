from __future__ import annotations

import argparse
import sys

from modules.config import DEFAULT_OUTPUT, DEFAULT_PINGOUT, Settings
from modules.helpers import contains_control_chars, error, is_positive_integer


# Route parser errors through project logging helpers for consistent UX.
class ReconArgParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        error(message)
        raise SystemExit(1)


def build_parser(prog: str) -> argparse.ArgumentParser:
    parser = ReconArgParser(
        prog=prog,
        description="Reconnoisseur v1.0.0 (https://github.com/daFinndus/reconnoisseur)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # This is target related
    target_group = parser.add_argument_group("Target")
    target_group.add_argument(
        "-t",
        required=True,
        dest="target",
        metavar="HOST or SUBNET",
        help="Target IPv4, hostname, or IPv4 CIDR range.",
    )
    target_group.add_argument(
        "-pt",
        dest="pingout",
        metavar="SECONDS",
        help="Host reachability timeout in seconds (Validation fallback: 10).",
    )

    # This is related to the nmap scan
    scan_group = parser.add_argument_group("Scan Behavior")
    scan_group.add_argument(
        "-fp",
        dest="full_ports",
        action="store_true",
        help="Scan all 65535 TCP ports (Default: top 1000).",
    )
    scan_group.add_argument(
        "-nss",
        dest="no_service_scan",
        action="store_true",
        help="Skip follow-up service detection scan.",
    )
    scan_group.add_argument(
        "-y",
        dest="yes",
        action="store_true",
        help="Skip confirmation prompts.",
    )

    # This is for the project and output configuration
    output_group = parser.add_argument_group("Output and Project")
    output_group.add_argument(
        "-o",
        dest="output",
        metavar="DIR",
        help="Custom output directory for results.",
    )
    output_group.add_argument(
        "-pn",
        dest="project_name",
        metavar="NAME",
        help="Project name; skips interactive init naming.",
    )

    # This modifies script behaviour
    runtime_group = parser.add_argument_group("Runtime")
    runtime_group.add_argument(
        "-ns",
        dest="no_save",
        action="store_true",
        help="Disable saving the scan results, logs, etc. to the output.",
    )
    runtime_group.add_argument(
        "-v",
        dest="verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    runtime_group.add_argument(
        "-ncc",
        dest="no_color_check",
        action="store_true",
        help="Disable color support check.",
    )
    runtime_group.add_argument(
        "-nd",
        dest="no_delay",
        action="store_true",
        help="Disable chat message delay.",
    )

    return parser


# Parse CLI arguments and update shared runtime settings.
def parse_args(argv: list[str], settings: Settings) -> None:
    parser = build_parser(sys.argv[0])
    parsed_args = parser.parse_args(argv)

    # Check if pingout is a valid positive integer, if provided.
    if parsed_args.pingout and not is_positive_integer(parsed_args.pingout):
        error("The ping timeout must be a positive integer, using default.")
        parsed_args.pingout = ""

    # Check if output is valid, if provided.
    if parsed_args.output and contains_control_chars(parsed_args.output):
        error(
            "The output directory contains unsupported control characters, using default."
        )
        parsed_args.output = ""

    # Check if project name seems good, if provided.
    if parsed_args.project_name and contains_control_chars(parsed_args.project_name):
        error(
            "The project name contains unsupported control characters, using default."
        )
        parsed_args.project_name = ""

    settings.target = parsed_args.target
    settings.pingout = parsed_args.pingout or str(DEFAULT_PINGOUT)
    settings.full_port_scan = parsed_args.full_ports
    settings.service_scan = not parsed_args.no_service_scan
    settings.yes = parsed_args.yes
    settings.output = parsed_args.output or str(DEFAULT_OUTPUT)
    settings.color_check = not parsed_args.no_color_check
    settings.project_name = parsed_args.project_name or ""
    settings.verbose = parsed_args.verbose
    settings.save = not parsed_args.no_save
    settings.delay = not parsed_args.no_delay
