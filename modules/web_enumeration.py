from __future__ import annotations

import http.client
import socket
import ssl

from modules.helpers import info, success, warn
from modules.nmap import extract_ports
from modules.config import Settings

WEB_SERVICE_HINTS = {
    "http",
    "https",
    "http-proxy",
    "ssl/http",
    "sun-answerbook",
    "http-alt",
    "http-mgmt",
    "webcache",
}

def looks_like_http(response: http.client.HTTPResponse) -> bool:
    if not (100 <= response.status <= 599):
        return False

    header_names = {name.lower() for name in response.headers.keys()}
    expected_headers = {"server", "location", "content-type", "set-cookie"}
    
    return bool(header_names & expected_headers) or response.status in {200, 301, 302, 401, 403}


def probe_http(host: str, port: int, use_tls: bool, timeout: float = 2.5) -> bool:
    connection: http.client.HTTPConnection | http.client.HTTPSConnection

    try:
        if use_tls:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            connection = http.client.HTTPSConnection(host, port=port, timeout=timeout, context=context)
        else:
            connection = http.client.HTTPConnection(host, port=port, timeout=timeout)

        connection.request("HEAD", "/", headers={"Host": host, "User-Agent": "Reconnoisseur/1.0"})
        response = connection.getresponse()
        return looks_like_http(response)
    except (http.client.HTTPException, OSError, socket.timeout, ssl.SSLError):
        return False
    finally:
        try:
            connection.close()
        except Exception:
            pass


def extract_webserver(settings: Settings) -> list[str]:
    discovered: list[str] = []
    
    gnmap_file = f"{settings.output}/{settings.project_name}/nmap/{settings.target}.gnmap"

    try:
        open_ports = extract_ports(gnmap_file)
    except FileNotFoundError:
        warn(f"Could not find gnmap file {gnmap_file}. Skipping web extraction.")
        return []

    if not open_ports:
        info("No open TCP ports found in gnmap output.")
        return []
    
    open_ports = open_ports.split(", ")

    # Probe likely web ports first to speed up detection, then test the rest.
    high_conf = [(host, port, svc) for host, port, svc in open_ports if svc in WEB_SERVICE_HINTS]
    low_conf = [(host, port, svc) for host, port, svc in open_ports if svc not in WEB_SERVICE_HINTS]

    for host, port, service in high_conf + low_conf:
        http_ok = probe_http(host, int(port), use_tls=False)
        https_ok = probe_http(host, int(port), use_tls=True)

        if not http_ok and not https_ok:
            continue

        if http_ok:
            discovered.append(f"http://{host}:{port}")
        if https_ok:
            discovered.append(f"https://{host}:{port}")

    # Preserve order while removing duplicates.
    unique_discovered = list(dict.fromkeys(discovered))

    if unique_discovered:
        success(f"Detected {len(unique_discovered)} reachable web endpoint(s).")
    else:
        info("No reachable web endpoints detected from open TCP ports.")

    return unique_discovered

def check_prerequisites() -> bool:
    return True