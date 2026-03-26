# This script contains functions which are run at the end, e.g. for cleanup, summary.
# -----------------------------------------------------------------------------------

from modules.helpers import info, step, warn, success


def summarize(ports: dict[str, dict[str, str]], web: dict[str, dict]) -> None:
    step("Summarizing the results now...")

    ports = ports or {}
    web = web or {}

    if not ports:
        info("No hosts or open ports were discovered. Nothing to summarize.")
        return

    hosts = len(ports)
    open_ports = sum(len(p) for p in ports.values())
    web_hits = len(web)

    info(f"{hosts} hosts | {open_ports} open ports | {web_hits} web hits")

    for host in sorted(ports):
        host_ports = ports.get(host, {})

        step(host)

        for port in sorted(host_ports, key=int):
            service = host_ports[port] or "unknown"
            endpoint = f"{host}:{port}"
            data = web.get(endpoint)

            if not data:
                info(f"Port {port} running {service}")
                continue

            scheme = data.get("scheme", "http")
            status = data.get("status_code", "?")
            redirect = data.get("redirect_target") or data.get("custom_host")
            arrow = f" -> {redirect}" if redirect else ""

            line = f"Port {port} running {service} - {scheme} {status}{arrow}"

            if isinstance(status, int) and status >= 400:
                warn(line)
            elif redirect:
                warn(line)
            else:
                success(line)
