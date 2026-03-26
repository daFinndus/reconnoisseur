# Reconnoisseur

Reconnoisseur is a modular Python reconnaissance toolkit that:

- validates a host or subnet target,
- checks system/tool dependencies,
- runs Nmap-based host and port discovery,
- optionally runs service detection scans,
- optionally probes discovered HTTP(S) services,
- summarizes findings in a compact report.

## Disclaimer

Use this only against systems and networks you own or are explicitly authorized to assess.
You are solely responsible for legal and scope compliance.

## Requirements

- Python 3.10+

- `python-requests`
- `python-urllib3`
- `nmap`
- `ffuf`
- `ipcalc`
- `ip` command (from `iproute2` or equivalent)

- Package manager support for auto-install: `apt` or `yay`
- Elevated privileges (for package install and hostfile modification)

## Installation

```bash
git clone https://github.com/daFinndus/reconnoisseur.git
cd reconnoisseur
```

## Usage

Show help:

```bash
python3 reconnoisseur.py -h
```

Basic host scan:

```bash
sudo python3 reconnoisseur.py -t 10.10.0.10
```

Verbose scan with custom reachability timeout:

```bash
sudo python3 reconnoisseur.py -t example.com -pt 15 -v
```

Full TCP sweep (all ports) and no service detection:

```bash
sudo python3 reconnoisseur.py -t 10.10.0.10 -fp -nss
```

Subnet mode:

```bash
sudo python3 reconnoisseur.py -t 10.10.0.0/24
```

Non-interactive mode:

```bash
sudo python3 reconnoisseur.py -t 10.10.0.10 -y -pn my-project
```

## CLI Flags

| Flag | Description |
| --- | --- |
| `-t HOST or SUBNET` | Target hostname, IPv4, or IPv4 CIDR range (required) |
| `-pt SECONDS` | Reachability timeout for host checks |
| `-fp` | Scan all 65535 TCP ports instead of top 1000 |
| `-nss` | Skip service/version detection (`-sV -sC`) |
| `-y` | Skip confirmation prompts |
| `-o DIR` | Custom output directory |
| `-pn NAME` | Project name for workspace creation |
| `-ns` | Disable saving output files |
| `-v` | Enable verbose logging and pass `-v` to Nmap |
| `-ncc` | Skip color output check |
| `-nd` | Disable message delay |
| `-h` | Show help |

## Project Layout

```text
reconnoisseur.py          Main entrypoint and workflow orchestration
modules/
  config.py               Shared runtime settings/dataclass defaults
  parser.py               CLI parsing and runtime settings population
  system.py               Package manager detection and dependency checks
  target.py               Target validation and reachability checks
  init.py                 Output/workspace initialization
  nmap.py                 Host discovery, port scans, service scans, parsing
  web_enumeration.py      HTTP(S) probing and optional /etc/hosts updates
  finish.py               Final summary output
  helpers.py              Logging helpers, timestamps, pacing controls
tests/
  webserver.py            Local redirect test server helper
output/                   Generated scan artifacts (workspace per run)
```

## Runtime Flow

1. Parse CLI arguments into shared settings.
2. Optionally run terminal color sanity check.
3. Detect package manager (`apt` or `yay`).
4. Verify/install required dependencies.
5. Validate target format and reachability.
6. Initialize workspace (unless `-ns` disables saving).
7. Run Nmap port scan workflow:
   - host mode: scan single target
   - subnet mode: discover live hosts, then scan each host
8. Optionally run service detection scans (`-sV -sC`) on discovered open ports.
9. Probe web-capable services and capture response metadata.
10. Print a final summary of hosts, ports, and web probe results.

## Output

When saving is enabled, scan artifacts are written to:

```text
output/<project-name>/nmap/
```

Generated files include standard Nmap formats:

- `.nmap`
- `.gnmap`
- `.xml`

In subnet mode, discovered hosts are also written to `hosts.txt`.

## Notes

- CIDR scanning requires your machine to be in a compatible local subnet.
- `-y` suppresses safety prompts; use carefully.
- Web probing currently keys off discovered service names containing `http`.
- Redirect handling may attempt to append resolved hostnames to `/etc/hosts`.
