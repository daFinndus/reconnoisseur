# This script contains functions which are run at the end, e.g. for cleanup, summary.
# -----------------------------------------------------------------------------------

from __future__ import annotations

from modules.helpers import info, step

PURPLE = "\033[35m"
RESET = "\033[0m"


# A simple helper to print the summary header and results in a consistent format.
def summary(message: str = "") -> None:
    print(f"{PURPLE}{message}{RESET}")


# Print a compact summary of discovered ports/services and web probe findings.
def summarize(ports: dict[str, dict[str, str]], web: dict[str, dict]) -> None:
    ports = ports or {}
    web = web or {}

    if not ports:
        info("No hosts or open ports were discovered. Nothing to summarize.")
        return

    print()
    step("Summarizing reconnaissance results...")

    hosts = len(ports)
    open_ports = sum(len(host_ports) for host_ports in ports.values())
    web_hits = len(web)

    summary(f"Hosts: {hosts}")
    summary(f"Open ports: {open_ports}")
    summary(f"Web endpoints: {web_hits}")

    for host in sorted(ports):
        host_ports = ports.get(host, {})
        summary(f"Host {host}")

        if not host_ports:
            summary(" - No open ports")
            continue

        for port in sorted(host_ports, key=int):
            service = host_ports[port] or "Unknown service"
            endpoint = f"{host}:{port}"
            data = web.get(endpoint)

            if not data:
                summary(f"  - {port}/tcp  {service}")
                continue

            scheme = data.get("scheme", "http")
            status_code = data.get("status_code", "?")
            line = f"  - {port}/tcp  {service}  [{scheme} {status_code}]"

            redirect_target = data.get("redirect_target")
            custom_host = data.get("custom_host")

            if redirect_target:
                line += f" -> {redirect_target}"
            elif custom_host:
                line += f" (host: {custom_host})"

            summary(line)
