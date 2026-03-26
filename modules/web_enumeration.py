from __future__ import annotations

import subprocess
from urllib.parse import urljoin, urlparse

import requests
import urllib3

from modules.config import Settings
from modules.helpers import error, info, log, step, success, timestamp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _schemes(service: str) -> list[str]:
    service_name = service.lower()

    if "https" in service_name:
        return ["https", "http"]

    return ["http", "https"]


def probe_web_services(
    settings: Settings,
    services: dict[str, dict[str, str]],
) -> dict[str, dict]:
    log(f"Just checking up, this is provided:\n\n{services}\n")

    if not settings.yes:
        confirmation = input(f"[{timestamp()}] Do you wanna do web enumeration? (y/N) ")

        if confirmation != "y":
            info("Skipping web enumeration.")
            return {}
    else:
        log("Skipping confirmation prompt, doing web enumeration!")

    results: dict[str, dict] = {}

    for ip_address, ports in services.items():
        log(f"Looking in {ip_address} for web services.")

        for port, service in ports.items():
            endpoint = f"{ip_address}:{port}"
            log(f"Searching through {ip_address}:{port} for web services...")

            if "http" not in service.lower():
                log(f"Skipping non-web service on {ip_address}:{port}!")
                log(f"http not found in service name '{service}', skipping.")
                continue

            log(f"Found potential web service on {ip_address}:{port}.")

            for scheme in _schemes(service):
                probe_url = f"{scheme}://{ip_address}:{port}"
                log(f"Probing {probe_url}.")

                try:
                    # First request without following redirects.
                    # This is to detect if there are hostname redirects.
                    response = requests.get(
                        probe_url,
                        verify=False,
                        allow_redirects=False,
                        timeout=5,
                    )

                    log(f"Got following response status: {response.status_code}")

                    item: dict[str, object] = {
                        "scheme": scheme,
                        "status_code": response.status_code,
                    }

                    if response.is_redirect:
                        log("Redirect detected!")

                        location_header = response.headers.get("Location", "")

                        redirect_target = (
                            urljoin(probe_url, location_header)
                            if location_header
                            else ""
                        )

                        redirect_hostname = urlparse(redirect_target).hostname or ""

                        if redirect_target:
                            log(f"Detected redirect target: {redirect_target}.")
                            item["redirect_target"] = redirect_target

                        if redirect_hostname and redirect_hostname != ip_address:
                            modify_hostfile(redirect_hostname, ip_address)
                            item["custom_host"] = redirect_hostname

                        log(
                            "Final host after redirects: "
                            f"{redirect_target or redirect_hostname or 'unknown'}."
                        )
                    else:
                        log("No redirect detected, seems like a normal web service.")

                    results[endpoint] = item
                    break
                except requests.exceptions.SSLError:
                    log(f"TLS handshake failed for {probe_url}, trying fallback.")
                    continue
                except requests.exceptions.ConnectionError:
                    error("Couldn't connect to webservice!")
                    continue
                except requests.exceptions.Timeout:
                    error("Can't reach webserver, timed out!")
                    continue
                except requests.exceptions.RequestException as exc:
                    error(f"Unexpected web probe error: {exc}")
                    continue

        success(f"Finished probing {ip_address} for web services.")
    return results


def modify_hostfile(hostname: str, ip_address: str) -> None:
    step(f"Adding hostname {hostname} to hosts file.")

    cleaned_hostname = hostname.strip()

    if not cleaned_hostname or cleaned_hostname == ip_address:
        return

    hosts_path = "/etc/hosts"

    try:
        with open(hosts_path, "r", encoding="utf-8") as handle:
            # Read the whole hostfile for checking and rewriting.
            lines = handle.readlines()

        # Check if the hostname already exists in the hosts file.
        for line in lines:
            fields = line.split()

            if cleaned_hostname in fields[1:]:
                log(f"Hostname {cleaned_hostname} already exists.")
                return

        # Write to temporary host file because direct modification is not allowed.
        with open("/tmp/hosts.tmp", "w", encoding="utf-8") as handle:
            for line in lines:
                handle.write(line)

            handle.write(f"{ip_address}\t{cleaned_hostname}\n")
            log("Wrote new entry to temporary hosts file.")

        # Then move the newly modified file back to /etc/hosts with sudo permissions.
        subprocess.run(["sudo", "mv", "/tmp/hosts.tmp", hosts_path], check=True)

        success(f"{cleaned_hostname} with IP {ip_address} is in {hosts_path}.")

    except Exception as exc:
        error(f"Failed to modify hosts file: {exc}")
