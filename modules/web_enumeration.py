from __future__ import annotations

import http.client
import socket
import ssl

from modules.helpers import info, success


def looks_like_http(response: http.client.HTTPResponse) -> bool:
    if not (100 <= response.status <= 599):
        return False

    header_names = {name.lower() for name in response.headers.keys()}
    expected_headers = {"server", "location", "content-type", "set-cookie"}

    return bool(header_names & expected_headers) or response.status in {
        200,
        301,
        302,
        401,
        403,
    }


def probe_http(host: str, port: int, use_tls: bool, timeout: float = 2.5) -> bool:
    connection: http.client.HTTPConnection | http.client.HTTPSConnection

    try:
        if use_tls:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            connection = http.client.HTTPSConnection(
                host, port=port, timeout=timeout, context=context
            )
        else:
            connection = http.client.HTTPConnection(host, port=port, timeout=timeout)

        connection.request(
            "HEAD", "/", headers={"Host": host, "User-Agent": "Reconnoisseur/1.0"}
        )
        response = connection.getresponse()
        return looks_like_http(response)
    except (http.client.HTTPException, OSError, socket.timeout, ssl.SSLError):
        return False
    finally:
        try:
            connection.close()
        except Exception:
            pass


def extract_webserver(ports: dict[str, str]) -> list[str]:
    discovered: list[str] = []

    return []


def check_prerequisites() -> bool:
    return True
