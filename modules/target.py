from __future__ import annotations

import re
import subprocess

from modules.config import Settings
from modules.helpers import contains_control_chars, error, info, log, step, success


# Validate target syntax and then verify reachability.
# For CIDR targets this also confirms the host is in a compatible local subnet.
def validate_target(settings: Settings) -> None:
    step("Validating the target now...")

    if any(character.isspace() for character in settings.target):
        error("The target must not contain whitespaces.")
        raise SystemExit(1)

    if contains_control_chars(settings.target):
        error("The target contains unsupported control characters.")
        raise SystemExit(1)

    if not is_valid_target(settings.target):
        error("The target must be a valid IPv4 address, hostname, or IPv4 CIDR range.")
        raise SystemExit(1)

    log(f"Target {settings.target} looks good, let's see if it's reachable.")

    step("Checking reachability of the target...")

    if "/" in settings.target:
        check_subnet_compatibility(settings)
    else:
        check_host_reachability(settings)


def check_subnet_compatibility(settings: Settings) -> None:
    log("Seems you are using a subnet, checking compatibility...")

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

    log(f"Found the following local subnets: {' '.join(local_subnets)}.")

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
            subnet = fields[1] if fields else ""
            break

    if subnet in local_subnets:
        success("You are in the same subnet as the provided target, good job!")
        settings.subnet = True

        return

    log(f"The target is in {subnet} and you're in {' '.join(local_subnets)}.")
    error("Please make sure you are in the same subnet as the target.")

    raise SystemExit(1)


def check_host_reachability(settings: Settings) -> None:
    log("The target is a single host, checking if it's reachable.")

    args = ["nmap", settings.target, "-sn", "--host-timeout", settings.pingout]

    log(f"Running nmap with the following command:\n\n {' '.join(args)}\n")

    ping_result = subprocess.run(args, capture_output=True, text=True, check=False)

    log(f"This here is the response:\n\n{ping_result.stdout}")

    if "Host is up" in ping_result.stdout:
        log(f"The target {settings.target} is reachable, good job!")
        return
    else:
        log(f"The target {settings.target} is not reachable.")
        log(f"The nmap scan result was {ping_result.returncode}.")

    error(f"The target {settings.target} is not reachable.")
    raise SystemExit(1)


# Validate that a string is a properly ranged IPv4 address.
def is_valid_ipv4(candidate: str) -> bool:
    if not re.fullmatch(r"([0-9]{1,3}\.){3}[0-9]{1,3}", candidate):
        return False

    octets = candidate.split(".")
    return all(0 <= int(octet) <= 255 for octet in octets)


# Validate a DNS hostname using common label rules.
def is_valid_hostname(candidate: str) -> bool:
    if len(candidate) > 253:
        return False

    return bool(
        re.fullmatch(
            r"[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*",
            candidate,
        )
    )


# Validate a target as IPv4, hostname, or IPv4 CIDR.
def is_valid_target(candidate: str) -> bool:
    if "/" in candidate:
        address, prefix = candidate.rsplit("/", maxsplit=1)

        log(f"Got address {address} and prefix {prefix} from the provided CIDR.")

        if not is_valid_ipv4(address):
            return False

        if not prefix.isdigit():
            return False

        return 0 <= int(prefix) <= 32

    return is_valid_ipv4(candidate) or is_valid_hostname(candidate)
