from __future__ import annotations

import re
import subprocess

from pathlib import Path

from modules.config import Settings
from modules.helpers import error, info, step, success, timestamp, warn


# Sanitize a target string so it is safe to use in filenames.
def sanitize_scan_name(value: str) -> str:
    value = value.replace("/", "_").replace(":", "_").replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9._-]", "_", value)


class Nmap:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        self.hosts: list[str] = []  # This will hold discovered or the provided host.
        # host -> {port -> detected service name (can be empty when unknown)}
        self.ports: dict[str, dict[str, str]] = {}

        self.nmap_dir = Path("/tmp")

    # Run the high-level port scanning flow for a host or subnet target.
    def portscan(self) -> bool:
        step("Proceeding with the port scan!")

        if self.settings.save:
            self.nmap_dir = Path(f"{self.settings.workspace}/nmap")
            self.nmap_dir.mkdir(parents=True, exist_ok=True)

            success("Created the nmap directory in the workspace!")
        else:
            warn("Saving is disabled, the nmap scan results won't be stored.")

        if self.settings.subnet:
            info("Subnet mode is enabled, discovering live hosts and scanning them...")

            if not self.scan_subnet_hosts():
                error(f"Subnet scanning failed for {self.settings.target}.")
                return False
        else:
            # Store the host in the list.
            # I am doing it like this, so implementing multiple hosts in the future is easier.
            self.hosts.append(self.settings.target)

            if not self.scan_host_ports(self.hosts[0]):
                error(f"Host scanning failed for {self.hosts[0]}.")
                return False

        # Delete the temporary file if saving is disabled.
        if not self.settings.save:
            gnmap_file = f"/tmp/temporary.gnmap"

            Path(gnmap_file).unlink(missing_ok=True)
            success("Deleted the temporary .gnmap file again.")

        success(f"Port scanning finished.")

        return True

    # Discover live hosts in a subnet and scan each host individually.
    # Writes discovered hosts to a log file and uses the last octet for per-host output names.
    def scan_subnet_hosts(self) -> bool:
        output_file = self.nmap_dir / "subnet"

        if self.settings.save:
            info(f"Going to use subnet as the base name for nmap output files.")

        if not self.settings.yes:
            confirm = input(f"[{timestamp()}] Do you want to continue? (y/N) ")

            if confirm != "y":
                error("Operation cancelled by user.")
                return False
        else:
            warn("Skipping confirmation prompt for output name, be careful with that!")

        info(f"Discovering live hosts inside {self.settings.target} first.")

        args = ["-sn", self.settings.target]

        if not self.run_nmap_scan(str(output_file), *args):
            error(f"Host discovery failed for {self.settings.target}.")
            return False

        self.hosts = self.extract_live_hosts(f"{str(output_file)}.gnmap")

        if not self.hosts:
            warn(f"No live hosts were discovered in {self.settings.target}.")
            return True

        print()
        success(f"Discovered {len(self.hosts)} live host(s).")

        if self.settings.save:
            hosts_file = Path(f"{self.nmap_dir}/hosts.txt")
            hosts_file.write_text("\n".join(self.hosts) + "\n", encoding="utf-8")

            success(f"Saved the list of discovered hosts to hosts.txt.")

        for host in self.hosts:
            step(f"Scanning discovered host {host}")

            if not self.scan_host_ports(host):
                return False

        return True

    # Run a port scan for one host, show open ports, then optionally run service detection.
    def scan_host_ports(self, host: str) -> bool:
        output_name = sanitize_scan_name(host)
        output_dir = self.nmap_dir / output_name

        if self.settings.save:
            info(f"Going to use {output_name} as the name for nmap output files.")

        if not self.settings.yes:
            confirm = input(f"[{timestamp()}] Do you wanna run nmap on {host}? (y/N) ")

            if confirm != "y":
                info(f"Skipping {host} as requested.")
                return True
        else:
            warn(f"Skipping confirmation prompt again, scanning {host}!")

        if self.settings.full_port_scan:
            info(f"Scanning all TCP ports on {host}. This may take a while.")

            args = ["-Pn", "-p-", host]

            if not self.run_nmap_scan(str(output_dir), *args):
                error(f"Port scan failed for {host}.")
                return False
        else:
            info(f"Scanning nmap's default top 1000 TCP ports on {host}.")

            args = ["-Pn", host]

            if not self.run_nmap_scan(str(output_dir), *args):
                error(f"Port scan failed for {host}.")
                return False

        self.extract_ports(host, f"{str(output_dir)}.gnmap")

        print()

        if self.ports.get(host):
            ports = ",".join(sorted(self.ports[host], key=int))
            success(f"Open TCP ports on {host}: {ports}.")
        else:
            warn(f"No open TCP ports found on {host}.")

        if not self.run_service_scan(host):
            error(f"Service detection failed for {host}.")
            return False

        return True

    # Run follow-up service/version detection on discovered open ports.
    def run_service_scan(self, host: str) -> bool:
        output_name = f"{sanitize_scan_name(host)}-service"
        output_dir = self.nmap_dir / output_name

        if not self.settings.service_scan:
            info(f"Skipping service detection for {host}, disabled via CLI option.")
            return True

        host_ports = self.ports.get(host, {})
        ports = ",".join(sorted(host_ports, key=int))

        if not ports:
            warn(f"Skipping service scan for {host}, no open TCP ports were found.")
            return True

        info(f"Running service detection against {host} on ports {ports}.")

        args = ["-Pn", "-sV", "-sC", "-p", ports, host]

        if not self.run_nmap_scan(str(output_dir), *args):
            error(f"Service detection scan failed for {host}.")
            return False

        # Parse service scan output to enrich port -> service mapping.
        self.extract_ports(host, f"{str(output_dir)}.gnmap")

        print()

        if self.settings.save:
            success(f"Saved service detection results to .nmap, .gnmap and .xml.")

        return True

    # Execute an nmap command with shared flags and output handling.
    def run_nmap_scan(self, output: str, *args: str) -> bool:
        cmd = ["nmap"]
        cmd.extend(args)

        if self.settings.save:
            cmd.extend(["-oA", output])
        else:
            # If saving is disabled, write the .gnmap output to a temporary file for parsing and delete it again later.
            cmd.extend(["-oG", f"/tmp/temporary.gnmap"])

        if self.settings.verbose:
            cmd.append("-v")

        # Print newline so the nmap scan is presented clearly
        print()

        result = subprocess.run(cmd, check=False)

        return result.returncode == 0

    # Parse a .gnmap file and return unique open TCP ports as a comma-separated list.
    def extract_ports(self, host: str, gnmap_file: str) -> str:
        ports: dict[str, str] = {}

        if not self.settings.save:
            gnmap_file = f"/tmp/temporary.gnmap"

        try:
            with open(gnmap_file, "r", encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    if "Ports: " not in line:
                        continue

                    blob = line.split("Ports: ", maxsplit=1)[1].strip()

                    for entry in blob.split(", "):
                        fields = entry.split("/")

                        if (
                            len(fields) >= 5
                            and fields[1] == "open"
                            and fields[0].isdigit()
                        ):
                            ports[fields[0]] = fields[4]
        except FileNotFoundError:
            return ""

        parsed_ports = ",".join(sorted(ports, key=int))
        self.ports[host] = ports
        return parsed_ports

    # Parse a .gnmap file and return hosts marked as up.
    def extract_live_hosts(self, gnmap_file: str) -> list[str]:
        self.hosts: list[str] = []

        if not self.settings.save:
            gnmap_file = f"/tmp/temporary.gnmap"

        try:
            with open(gnmap_file, "r", encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    if "Status: Up" not in line:
                        continue

                    fields = line.split()

                    if len(fields) >= 2:
                        self.hosts.append(fields[1])
        except FileNotFoundError:
            return []

        return self.hosts
