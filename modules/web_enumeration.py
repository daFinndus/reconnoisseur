import requests
import urllib3

from urllib.parse import urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def probe_web_services(services: dict) -> dict:
    results = {}

    for ip, ports in services.items():
        for port, service in ports.items():
            if "http" not in service.lower():
                continue

            # Determine scheme from service name, fall back to trying both
            schemes = (
                ["https", "http"] if service.lower() == "https" else ["http", "https"]
            )

            for scheme in schemes:
                url = f"{scheme}://{ip}:{port}"
                try:
                    response = requests.get(
                        url, timeout=5, verify=False, allow_redirects=True
                    )

                    final_url = response.url
                    final_host = urlparse(final_url).hostname
                    redirect_detected = final_host != ip

                    results[f"{ip}:{port}"] = {
                        "scheme": scheme,
                        "status_code": response.status_code,
                        "final_url": final_url,
                        "redirect_to_custom_host": redirect_detected,
                        "custom_host": final_host if redirect_detected else None,
                        "redirect_chain": [r.url for r in response.history],
                    }
                    break

                except requests.exceptions.SSLError:
                    continue
                except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                ):
                    break

    return results
