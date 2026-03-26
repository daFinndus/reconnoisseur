from __future__ import annotations

import shutil
import subprocess
import importlib.util

from modules.config import Settings
from modules.helpers import error, info, log, step, success, timestamp, warn


# Detect which supported package manager is available.
def check_pkg_manager(settings: Settings) -> None:
    step("Checking for package manager...")
    log("Currently only apt and yay are supported!")

    apt_path = shutil.which("apt")
    yay_path = shutil.which("yay")

    if apt_path:
        settings.manager = "apt"
    elif yay_path:
        settings.manager = "yay"
    else:
        error("No supported package manager found.")
        raise SystemExit(1)

    success(f"Identified {settings.manager} as the package manager.")


# Ensure required tools exist and offer interactive installation when missing.
# Installs with the detected package manager and fails fast if installation did not succeed.
def check_pkgs(settings: Settings) -> None:
    dependencies = [
        {
            "name": "nmap",
            "kind": "bin",
            "check": "nmap",
            "pkg": {"apt": "nmap", "yay": "nmap"},
        },
        {
            "name": "ffuf",
            "kind": "bin",
            "check": "ffuf",
            "pkg": {"apt": "ffuf", "yay": "ffuf"},
        },
        {
            "name": "ipcalc",
            "kind": "bin",
            "check": "ipcalc",
            "pkg": {"apt": "ipcalc", "yay": "ipcalc"},
        },
        {
            "name": "requests",
            "kind": "py",
            "check": "requests",
            "pkg": {"apt": "python3-requests", "yay": "python-requests"},
        },
        {
            "name": "urllib3",
            "kind": "py",
            "check": "urllib3",
            "pkg": {"apt": "python3-urllib3", "yay": "python-urllib3"},
        },
        {
            "name": "rich",
            "kind": "py",
            "check": "rich",
            "pkg": {"apt": "python3-rich", "yay": "python-rich"},
        },
    ]

    step("Checking for required packages...")
    apt_index_updated = False

    for dependency in dependencies:
        module_name = dependency["check"]
        dependency_kind = dependency["kind"]
        is_installed = (
            importlib.util.find_spec(module_name) is not None
            if dependency_kind == "py"
            else shutil.which(module_name) is not None
        )

        if is_installed:
            log(f"Dependency {dependency['name']} is installed.")
            continue

        package_name = dependency["pkg"][settings.manager]
        warn(
            f"Dependency {dependency['name']} is missing. Installing {package_name}..."
        )

        if not settings.yes:
            answer = input(
                f"[{timestamp()}] Do you want to install {package_name}? (y/N) "
            )

            if answer != "y":
                error(f"Dependency {dependency['name']} is required. Exiting.")
                raise SystemExit(1)
        else:
            warn(f"Skipping confirmation prompt, installing {package_name}!")

        if settings.manager == "apt":
            if not apt_index_updated:
                subprocess.run(
                    ["sudo", "apt", "update"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
                apt_index_updated = True

            subprocess.run(
                ["sudo", "apt", "install", "-y", package_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        elif settings.manager == "yay":
            subprocess.run(
                ["yay", "-S", "--noconfirm", package_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

        is_installed = (
            importlib.util.find_spec(module_name) is not None
            if dependency_kind == "py"
            else shutil.which(module_name) is not None
        )

        if not is_installed:
            error(
                f"Failed to install {dependency['name']}. Please install it manually and re-run the script."
            )
            raise SystemExit(1)

        success(f"Dependency {dependency['name']} installed successfully.")

    success("Successfully installed all system dependencies.")
