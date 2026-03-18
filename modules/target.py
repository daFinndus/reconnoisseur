from __future__ import annotations

import re

from modules.helpers import info


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
        info(f"Got address {address} and prefix {prefix} from the provided CIDR notation.")

        if not is_valid_ipv4(address):
            return False

        if not prefix.isdigit():
            return False

        return 0 <= int(prefix) <= 32

    return is_valid_ipv4(candidate) or is_valid_hostname(candidate)