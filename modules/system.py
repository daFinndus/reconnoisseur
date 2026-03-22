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
    pkgs = ["nmap", "ffuf", "ipcalc", "python-requests", "python-urllib3"]

    step("Checking for required packages...")

    for pkg in pkgs:
        lookup_name = pkg

        if "python" in pkg:
            lookup_name = pkg.replace("python-", "")

            if importlib.util.find_spec(lookup_name) is not None:
                log(f"Python package {lookup_name} is installed.")
                continue
        else:
            if shutil.which(lookup_name):
                log(f"Package {pkg} is installed.")
                continue

        warn(f"Package {pkg} is not installed. Installing...")

        if not settings.yes:
            answer = input(f"[{timestamp()}] Do you want to install {pkg}? (y/N) ")

            if answer != "y":
                error(f"Package {pkg} is required. Exiting.")
                raise SystemExit(1)
        else:
            warn(f"Skipping confirmation prompt, installing {pkg}!")

        if settings.manager == "apt":
            subprocess.run(
                ["sudo", "apt", "update"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

            subprocess.run(
                ["sudo", "apt", "install", "-y", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        elif settings.manager == "yay":
            subprocess.run(
                ["yay", "-S", pkg],
                input="y\n",
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

        if "python" in pkg:
            if importlib.util.find_spec(lookup_name) is None:
                error(
                    f"Failed to install {pkg}. Please install it manually and re-run the script."
                )
                raise SystemExit(1)
        elif not shutil.which(lookup_name):
            error(
                f"Failed to install {pkg}. Please install it manually and re-run the script."
            )
            raise SystemExit(1)

        success(f"Package {pkg} installed successfully.")

    success("Successfully installed all system dependencies.")
