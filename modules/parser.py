from __future__ import annotations

import subprocess
import sys

from modules.config import DEFAULT_OUTPUT, DEFAULT_PINGOUT, Settings
from modules.helpers import contains_control_chars, error, info, is_positive_integer, step, success
from modules.target import is_valid_target


# Print CLI usage information.
def print_help(prog: str) -> None:
    print("Reconnoisseur v1.0.0 (https://github.com/daFinndus/reconnoisseur)")
    print(f"\nUsage: {prog} [options]")

    print("\nOptions:")
    print("\t-t, --target\t\tTarget domain or IP address.")
    print("\t-pt, --pingout\t\tTimeout for host reachability check in seconds (default: 10).")
    print("\t-fp, --full-ports\tScan all 65535 TCP ports instead of the default top 1000.")
    print("\t-nss, --no-service-scan\tSkip the follow-up service detection scan.")
    print("\t-y, --yes\t\tSkip all confirmation prompts, use with caution!")
    print()
    print("\t-o, --output\t\tSpecify a custom output directory for all results.")
    print()
    print("\t-ncc, --no-color-check\tDisable color support check, save some time.")
    print("\t-pn, --project-name\tSpecify the project name, skip whole init section.")
    print("\t-v, --verbose\t\tEnable verbose logging.")
    print("\t-nd, --no-delay\t\tDisable the delay after chat messages.")
    print(f"\nExample: {prog} -t 10.10.0.10 -pt 15 -v")


# Exit early when help is requested as the only argument.
def check_help(argv: list[str]) -> None:
    if len(argv) == 1 and argv[0] in {"-h", "--help"}:
        print_help(sys.argv[0])
        raise SystemExit(0)


# Ensure options that require a value actually received one.
def require_value(name: str, value: str | None) -> str:
    if not value:
        error(f"Option {name} requires a value.")
        raise SystemExit(1)
    
    return value


# Parse CLI arguments and update shared runtime settings.
def parse_args(argv: list[str], settings: Settings) -> None:
    i = 0
    while i < len(argv):
        arg = argv[i]

        if arg in {"-t", "--target"}:
            settings.target = require_value(arg, argv[i + 1] if i + 1 < len(argv) else None)
            i += 1
        elif arg in {"-pt", "--pingout"}:
            settings.pingout = require_value(arg, argv[i + 1] if i + 1 < len(argv) else None)
            i += 1
        elif arg in {"-fp", "--full-ports"}:
            settings.full_port_scan = True
        elif arg in {"-nss", "--no-service-scan"}:
            settings.service_scan = False
        elif arg in {"-y", "--yes"}:
            settings.yes = True
        elif arg in {"-o", "--output"}:
            settings.output = require_value(arg, argv[i + 1] if i + 1 < len(argv) else None)
            i += 1
        elif arg in {"-ncc", "--no-color-check"}:
            settings.color_check = False
        elif arg in {"-pn", "--project-name"}:
            settings.project_name = require_value(arg, argv[i + 1] if i + 1 < len(argv) else None)
            i += 1
        elif arg in {"-v", "--verbose"}:
            settings.verbose = True
        elif arg in {"-nd", "--no-delay"}:
            settings.delay = False
        elif arg in {"-h", "--help"}:
            error("Help option detected, please run without additional arguments!")
            raise SystemExit(1)
        else:
            error(f"Unknown parameter passed: {arg}.")
            raise SystemExit(1)

        i += 1

    if not settings.target:
        error("The target is required but was not provided. Specify via -t.")
        raise SystemExit(1)


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