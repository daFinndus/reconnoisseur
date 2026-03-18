from __future__ import annotations

import re
import time
from datetime import datetime

from modules.config import SETTINGS


COLORS = [
    "\033[31m",  # Red for errors
    "\033[33m",  # Yellow for warnings
    "\033[32m",  # Green for success
    "\033[34m",  # Blue for steps
    "\033[36m",  # Cyan for info
    "\033[0m",   # Reset color
]


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
    _sleep(1.5)


# Return True if the value is a positive integer string.
def is_positive_integer(value: str) -> bool:
    return bool(re.fullmatch(r"[1-9][0-9]*", value))


# Return True if the value includes control characters.
def contains_control_chars(value: str) -> bool:
    return any(ord(char) < 32 or ord(char) == 127 for char in value)