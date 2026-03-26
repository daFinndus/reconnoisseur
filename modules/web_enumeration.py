from __future__ import annotations

import subprocess
from urllib.parse import urljoin, urlparse

import requests
import urllib3

from modules.config import Settings
from modules.helpers import error, info, log, success, timestamp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

    results = {}

    for ip, ports in services.items():
        log(f"Looking in {ip} for webservices.")

        for port, service in ports.items():
            log(f"Searching through {ip}:{port} for web services...")

            if "http" not in service.lower():
                log(f"Skipping non-web service on {ip}:{port}!")
                log(f"http not found in service name '{service}', skipping.")
                continue

            log(f"Found potential web service on {ip}:{port}.")

            # Determine scheme from service name, fall back to trying both.
            schemes = ["https", "http"]

            for scheme in schemes:
                url = f"{scheme}://{ip}:{port}"
                log(f"Probing {url}.")

                try:
                    # First request without following redirects.
                    # This is to detect if there are hostname redirects.
                    response = requests.get(
                        url,
                        verify=False,
                        allow_redirects=False,
                        timeout=5,
                    )

                    log(f"Got following response status: {response.status_code}")

                    if response.is_redirect:
                        log("Redirect detected!")

                        redirect_target = ""
                        redirect_chain = []

                        location = response.headers.get("Location")

                        if location:
                            redirect_target = urljoin(url, location)
                            log(f"Detected redirect target: {redirect_target}.")

                        modify_hostfile(str(urlparse(redirect_target).hostname), ip)
                        log(f"Final host after redirects: {str(redirect_target)}.")

                        results[f"{ip}:{port}"] = {
                            "scheme": scheme,
                            "status_code": response.status_code,
                            "redirect_target": redirect_target,
                            "custom_host": (redirect_target),
                            "redirect_chain": redirect_chain,
                        }
                    else:
                        log("No redirect detected, seems like a normal web service.")

                        results[f"{ip}:{port}"] = {
                            "scheme": scheme,
                            "status_code": response.status_code,
                        }
                except requests.exceptions.SSLError:
                    error("Got a certificate error!")
                    continue
                except requests.exceptions.ConnectionError:
                    error("Couldn't connect to webservice!")
                    break
                except requests.exceptions.Timeout:
                    error("Can't reach webserver, timed out!")
                    continue
                except requests.exceptions.RequestException as exc:
                    error(f"Unexpected web probe error: {exc}")
                    continue

        success(f"Finished probing {ip} for web services.")
    return results


def modify_hostfile(hostname: str, ip: str) -> None:
    hosts_path = "/etc/hosts"

    try:
        with open(hosts_path, "r", encoding="utf-8") as f:
            # Read the whole hostfile for checking and rewriting.
            lines = f.readlines()

        # Check if the hostname already exists in the hosts file.
        for line in lines:
            if line.strip().endswith(hostname):
                log(f"Hostname {hostname} already exists in, skipping modification.")
                return

        # Write to temporary host file because direct modification is not allowed.
        with open("/tmp/hosts.tmp", "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line)
            f.write(f"{ip}\t{hostname}\n")

        # Then move the newly modified file back to /etc/hosts with sudo permissions.
        subprocess.run(["sudo", "mv", "/tmp/hosts.tmp", hosts_path], check=True)

        log(f"Added {hostname} with IP {ip} to {hosts_path}.")

    except Exception as exc:
        error(f"Failed to modify hosts file: {exc}")
