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


# Run the high-level port scanning flow for a host or subnet target.
def portscan(settings: Settings) -> bool:
    step("Proceeding with the port scan!")

    output_name = sanitize_scan_name(settings.target)
    info(f"Using {output_name} as the output name for {settings.target}.")

    nmap_dir = Path(settings.workspace) / "nmap"
    nmap_dir.mkdir(parents=True, exist_ok=True)
    success("Created the nmap directory in the workspace!")

    info(f"Doing an nmap scan on {settings.target} now...")
    output_directory = str(nmap_dir / output_name)

    if settings.subnet:
        info("Subnet mode is enabled, so the scan will discover live hosts and then scan each of them.")
        
        if not scan_subnet_hosts(settings, output_directory):
            return False
    else:
        if not scan_host_ports(settings, output_directory, settings.target):
            return False

    success(f"Port scanning finished. Results are stored in {settings.workspace}/nmap.")
    return True


# Run a port scan for one host, show open ports, then optionally run service detection.
def scan_host_ports(settings: Settings, output: str, host: str) -> bool:
    if not settings.yes:
        scan_confirm = input(f"[{timestamp()}] Do you wanna run a nmap scan on {host}? (y/n) ")
        
        if scan_confirm != "y":
            info(f"Skipping {host} as requested.")
            return True
    else:
        warn(f"Skipping confirmation prompt again, scanning {host}!")

    if settings.full_port_scan:
        info(f"Scanning all TCP ports on {host}. This may take a while.")
        
        if not run_nmap_scan(settings, output, "-Pn", "-p-", host):
            error(f"Port scan failed for {host}.")
            return False
    else:
        info(f"Scanning nmap's default top 1000 TCP ports on {host}.")
        
        if not run_nmap_scan(settings, output, "-Pn", host):
            error(f"Port scan failed for {host}.")
            return False

    ports = extract_ports(f"{output}.gnmap")

    print()

    if ports:
        success(f"Open TCP ports on {host}: {ports}")
    else:
        warn(f"No open TCP ports found on {host}.")

    return run_service_scan(settings, output, host, ports)


# Run follow-up service/version detection on discovered open ports.
def run_service_scan(settings: Settings, output: str, host: str, ports: str) -> bool:
    if not settings.service_scan:
        info(f"Skipping service detection for {host} because it was disabled via CLI option.")
        return True

    if not ports:
        warn(f"Skipping service detection for {host} because no open TCP ports were found.")
        return True

    info(f"Running service detection against {host} on ports {ports}.")
    if not run_nmap_scan(settings, f"{output}-service", "-Pn", "-sV", "-sC", "-p", ports, host):
        error(f"Service detection failed for {host}.")
        return False

    print()
    success(f"Saved service detection results to .nmap, .gnmap and .xml.")
    
    return True


# Discover live hosts in a subnet and scan each host individually.
# Writes discovered hosts to a log file and uses the last octet for per-host output names.
def scan_subnet_hosts(settings: Settings, output: str) -> bool:
    hosts_file = Path(settings.workspace) / "nmap" / "hosts.log"

    info(f"Discovering live hosts inside {settings.target} first.")
    
    if not run_nmap_scan(settings, output, "-sn", settings.target):
        error(f"Host discovery failed for {settings.target}.")
        return False

    hosts = extract_live_hosts(f"{output}.gnmap")
    
    if not hosts:
        warn(f"No live hosts were discovered in {settings.target}.")
        return True

    hosts_file.write_text("\n".join(hosts) + "\n", encoding="utf-8")

    print()
    success(f"Discovered {len(hosts)} live host(s). Saved the list to {hosts_file}.")

    for host in hosts:
        octet = host.split(".")[-1]
        step(f"Scanning discovered host {host}")
        
        if not scan_host_ports(settings, f"{output}-{octet}", host):
            return False

    return True


# Execute an nmap command with shared flags and output handling.
def run_nmap_scan(settings: Settings, output: str, *args: str) -> bool:
    cmd = ["nmap"]
    
    if settings.verbose:
        cmd.append("-v")
        
    cmd.extend(args)
    cmd.extend(["-oA", output])

    # Print newline so the nmap scan is presented clearly
    print()

    result = subprocess.run(cmd, check=False)
    return result.returncode == 0


# Parse a .gnmap file and return unique open TCP ports as a comma-separated list.
def extract_ports(gnmap_file: str) -> str:
    ports: set[int] = set()

    try:
        with open(gnmap_file, "r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                if "Ports: " not in line:
                    continue
                
                port_blob = line.split("Ports: ", maxsplit=1)[1].strip()
                
                for entry in port_blob.split(", "):
                    fields = entry.split("/")
                    
                    if len(fields) >= 2 and fields[1] == "open" and fields[0].isdigit():
                        ports.add(int(fields[0]))
    except FileNotFoundError:
        return ""

    return ",".join(str(port) for port in sorted(ports))


# Parse a .gnmap file and return hosts marked as up.
def extract_live_hosts(gnmap_file: str) -> list[str]:
    hosts: list[str] = []

    try:
        with open(gnmap_file, "r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                if "Status: Up" not in line:
                    continue
                
                fields = line.split()
                
                if len(fields) >= 2:
                    hosts.append(fields[1])
    except FileNotFoundError:
        return []

    return hosts
