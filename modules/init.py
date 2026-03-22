from __future__ import annotations

from pathlib import Path

from modules.config import DEFAULT_OUTPUT, Settings
from modules.helpers import error, info, log, step, success, timestamp, warn


# Show a quick terminal color preview unless disabled.
def check_colors(settings: Settings) -> None:
    step("Checking if the terminal displays colors correctly...")

    info("This should be blue.")
    success("This should be green.")
    warn("This should be yellowish.")
    error("This should be red.")

    info("The script can run without the colors being a 100% match.")


# Create base directories and the project workspace.
# If the workspace already exists, ask for confirmation unless auto-approve is enabled.
def init_workspace(settings: Settings) -> None:
    step("Creating necessary directories...")

    output_dir = Path(settings.output or DEFAULT_OUTPUT)
    output_dir.mkdir(parents=True, exist_ok=True)

    log("Made sure that the output directory exists.")

    if not settings.project_name:
        name = input(f"[{timestamp()}] Please give this project a name: ")
        info(f"Using {name} as the project name and creating workspace directories...")
    else:
        log("Project name provided via CLI, creating workspace...")

    settings.workspace = f"{output_dir}/{settings.project_name or name}"

    if Path(settings.workspace).exists():
        warn(f"Workspace {settings.project_name or name} already exists, using it...")
        warn("This will probably overwrite files!")

        if not settings.yes:
            answer = input(f"[{timestamp()}] Do you want to continue? (y/N) ")

            if answer != "y":
                error("Probably a good decision, good bye!")
                raise SystemExit(1)
        else:
            warn("Skipping confirmation prompt as requested, be careful with that!")

    Path(settings.workspace).mkdir(parents=True, exist_ok=True)

    success(f"The workspace is created in {settings.workspace}.")
