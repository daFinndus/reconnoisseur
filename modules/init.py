from __future__ import annotations

from pathlib import Path

from modules.config import DEFAULT_OUTPUT, Settings
from modules.helpers import error, info, step, success, timestamp, warn


# Show a quick terminal color preview unless disabled.
def check_colors(settings: Settings) -> None:
    if not settings.color_check:
        return

    step("Checking if the terminal displays colors correctly...")

    info("This should be blue.")
    success("This should be green.")
    warn("This should be yellowish.")
    error("This should be red.")

    info("The script can run without the colors being a 100% match.")


# Create base directories and the project workspace.
# If the workspace already exists, ask for confirmation unless auto-approve is enabled.
def init_workspace(settings: Settings) -> None:
    name = ""

    step("Creating necessary directories...")

    Path("output").mkdir(parents=True, exist_ok=True)
    success("Made sure that the output directory exists.")

    Path("wordlists").mkdir(parents=True, exist_ok=True)
    success("Also made sure that the wordlists directory exists.")

    if settings.project_name:
        info("Project name provided via CLI, creating workspace...")
    else:
        name = input(f"[{timestamp()}] Please give this project a name: ")
        info(f"Using {name} as the project name and creating workspace directories...")

    settings.workspace = f"{settings.output or DEFAULT_OUTPUT}/{settings.project_name or name}"

    workspace = Path(settings.workspace)
    
    if workspace.exists():
        warn(f"A workspace with the name {settings.project_name or name} already exists, using it...")
        warn("This will probably overwrite existing files, make sure nothing important is there!")

        if not settings.yes:
            answer = input(f"[{timestamp()}] Do you want to continue with this workspace? (y/n) ")
            
            if answer != "y":
                error("Probably a good decision, good bye!")
                raise SystemExit(1)
        else:
            warn("Skipping confirmation prompt as requested, be careful with that!")

    workspace.mkdir(parents=True, exist_ok=True)
    
    success("Workspace created!")
    info(f"The output directory for this project lies in {settings.workspace}.")