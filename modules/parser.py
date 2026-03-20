from __future__ import annotations

import argparse
import subprocess
import sys

from modules.config import DEFAULT_OUTPUT, DEFAULT_PINGOUT, Settings
from modules.helpers import contains_control_chars, error, info, is_positive_integer, step, success
from modules.target import is_valid_target


class ReconArgParser(argparse.ArgumentParser):
    # Route parser errors through project logging helpers for consistent UX.
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
        help="Host reachability timeout in seconds (validation fallback: 10).",
    )

    # This is related to the nmap scan
    scan_group = parser.add_argument_group("Scan Behavior")
    scan_group.add_argument(
        "-fp",
        dest="full_ports",
        action="store_true",
        help="Scan all 65535 TCP ports (default: top 1000).",
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
        "-ncc",
        dest="no_color_check",
        action="store_true",
        help="Disable color support check.",
    )
    runtime_group.add_argument(
        "-v",
        dest="verbose",
        action="store_true",
        help="Enable verbose logging.",
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
    args = parser.parse_args(argv)

    settings.target = args.target
    settings.pingout = args.pingout or ""
    settings.full_port_scan = args.full_ports
    settings.service_scan = not args.no_service_scan
    settings.yes = args.yes
    settings.output = args.output or ""
    settings.color_check = not args.no_color_check
    settings.project_name = args.project_name or ""
    settings.verbose = args.verbose
    settings.delay = not args.no_delay


# Validate target syntax and then verify reachability.
# For CIDR targets this also confirms the host is in a compatible local subnet.
def validate_target(settings: Settings) -> None:
    step("Validating the target now...")

    if any(ch.isspace() for ch in settings.target):
        error("The target must not contain whitespace.")
        raise SystemExit(1)
    
    if contains_control_chars(settings.target):
        error("The target contains unsupported control characters.")
        raise SystemExit(1)
    
    if not is_valid_target(settings.target):
        error("The target must be a valid IPv4 address, hostname, or IPv4 CIDR range.")
        raise SystemExit(1)

    success(f"Target {settings.target} looks good, let's see if it's reachable.")

    step("Checking reachability of the target...")

    if "/" in settings.target:
        info("Seems you are using a subnet, checking compatibility...")

        route_result = subprocess.run(
            ["ip", "route"],
            capture_output=True,
            text=True,
            check=False,
        )
        
        # Check subnets the host is in
        local_subnets = []
        
        for line in route_result.stdout.splitlines():
            first = line.split(maxsplit=1)[0] if line.split() else ""
            if "/" in first:
                local_subnets.append(first)

        info(f"Found the following local subnets: {' '.join(local_subnets)}.")

        # Check if the target is in any of the local subnets
        ipcalc_result = subprocess.run(
            ["ipcalc", "-n", settings.target],
            capture_output=True,
            text=True,
            check=False,
        )
        
        subnet = ""
        
        for line in ipcalc_result.stdout.splitlines():
            if "Network" in line:
                fields = line.split()
                subnet = fields[-1] if fields else ""
                break

        if subnet in local_subnets:
            success("You are in the same subnet as the provided target, good job!")
            settings.subnet = True
            return

        error("Please make sure you are in the same subnet as the target.")
        info(f"The target subnet is {subnet} and yours is {' '.join(local_subnets)}. Gotta check up on that.")
        
        raise SystemExit(1)

    info("The target is a single host, checking if it's reachable.")
    
    ping_result = subprocess.run(
        ["ping", "-c", "1", "-W", settings.pingout or str(DEFAULT_PINGOUT), settings.target],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    
    if ping_result.returncode == 0:
        success(f"The target {settings.target} is reachable. Proceeding with recon.")
        return

    error(f"The target {settings.target} is not reachable. Please check the address and try again.")
    raise SystemExit(1)


# Validate ping timeout and fall back to the default on invalid input.
def validate_pingout(settings: Settings) -> None:
    if not settings.pingout:
        info("No ping timeout specified, using default value of 10 seconds.")
    elif is_positive_integer(settings.pingout):
        success(f"Updated ping timeout: {settings.pingout} seconds.")
        return
    else:
        error("Please choose a positive number for the ping timeout!")
        info("Using default value of 10 seconds!")

    settings.pingout = str(DEFAULT_PINGOUT)


# Validate the output path and apply the default when omitted.
def validate_output(settings: Settings) -> None:
    if not settings.output:
        info("No output directory specified, using default value 'output'.")
        settings.output = DEFAULT_OUTPUT
        return
    
    if contains_control_chars(settings.output):
        error("The output directory contains unsupported control characters.")
        raise SystemExit(1)

    success(f"Updated output directory: {settings.output}.")
    info("Let's hope nothing breaks...")


# Validate the optional project name before workspace creation.
def validate_project_name(settings: Settings) -> None:
    if not settings.project_name:
        info("No project name specified, will ask for it during workspace initialization.")
        return
    
    if contains_control_chars(settings.project_name):
        error("The project name contains unsupported control characters.")
        raise SystemExit(1)

    success(f"Updated project name: {settings.project_name}.")
    info("Let's hope nothing breaks...")