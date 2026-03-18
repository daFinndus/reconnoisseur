from __future__ import annotations

from dataclasses import dataclass


DEFAULT_OUTPUT = "output"
DEFAULT_PINGOUT = 10


@dataclass
class Settings:
    target: str = ""
    subnet: bool = False
    output: str = ""
    project_name: str = ""
    workspace: str = ""
    verbose: bool = False
    full_port_scan: bool = False
    service_scan: bool = True
    pingout: str = ""
    delay: bool = True
    color_check: bool = True
    yes: bool = False
    manager: str = ""


SETTINGS = Settings()