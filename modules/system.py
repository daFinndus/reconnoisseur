from __future__ import annotations

import shutil
import subprocess

from modules.config import Settings
from modules.helpers import error, info, step, success, timestamp, warn


# Detect which supported package manager is available.
def check_pkg_manager(settings: Settings) -> None:
    step("Checking for package manager...")
    info("Currently only apt and yay are supported!")

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
    pkgs = ["nmap", "ffuf", "ipcalc"]

    step("Checking for required packages...")

    for pkg in pkgs:
        if shutil.which(pkg):
            success(f"Package {pkg} is installed.")
            continue

        warn(f"Package {pkg} is not installed. Installing...")

        if not settings.yes:
            answer = input(f"[{timestamp()}] Do you want to install {pkg}? (y/n) ")
            
            if answer != "y":
                error(f"Package {pkg} is required. Exiting.")
                raise SystemExit(1)
        else:
            warn(f"Skipping confirmation prompt, installing {pkg}!")

        if settings.manager == "apt":
            subprocess.run(["sudo", "apt", "update"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
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

        if not shutil.which(pkg):
            error(f"Failed to install {pkg}. Please install it manually and re-run the script.")
            raise SystemExit(1)

        success(f"Package {pkg} installed successfully.")

    info("Successfully installed all dependencies.")