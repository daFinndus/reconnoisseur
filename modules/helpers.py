from __future__ import annotations

import re
import time

from datetime import datetime

from modules.config import SETTINGS


# These colors are used for different message types to improve readability.
COLORS = [
    "\033[38;2;220;50;50m",
    "\033[38;2;220;180;0m",
    "\033[38;2;50;200;50m",
    "\033[38;2;50;120;220m",
    "\033[38;2;0;180;180m",
    "\033[0m",
]


# Return True if the value is a positive integer string.
def is_positive_integer(value: str) -> bool:
    return bool(re.fullmatch(r"[1-9][0-9]*", value))


# Return True if the value includes control characters.
def contains_control_chars(value: str) -> bool:
    return any(ord(char) < 32 or ord(char) == 127 for char in value)


# Return the current local time in HH:MM:SS format.
def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


# Sleep for the requested duration when delays are enabled.
def _sleep(seconds: float) -> None:
    if SETTINGS.delay:
        time.sleep(seconds)


# Print a primary step message and pause a bit longer.
def step(message: str) -> None:
    print(f"\n{COLORS[3]}[{timestamp()}] {COLORS[-1]}{message}")
    _sleep(1.0)


# Print an informational message.
def info(message: str) -> None:
    print(f"{COLORS[4]}[{timestamp()}] {COLORS[-1]}{message}")
    _sleep(0.5)


# Print a success message.
def success(message: str) -> None:
    print(f"{COLORS[2]}[{timestamp()}] {COLORS[-1]}{message}")
    _sleep(0.5)


# Print a warning message.
def warn(message: str) -> None:
    print(f"{COLORS[1]}[{timestamp()}] {COLORS[-1]}{message}")
    _sleep(0.5)


# Print an error message and pause slightly longer.
def error(message: str) -> None:
    print(f"{COLORS[0]}[{timestamp()}] {COLORS[-1]}{message}")
    _sleep(1.0)


# This is for verbosity logging.
def log(message: str) -> None:
    if SETTINGS.verbose:
        print(f"{COLORS[4]}[{timestamp()}] {COLORS[-1]}{message}")
        _sleep(0.5)
