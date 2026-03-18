# Reconnoisseur

Reconnoisseur is a modular Python-based reconnaissance toolkit. It validates a target, prepares a workspace, checks and installs required tools, runs an initial port scan, and optionally performs service detection from a single command.

## Disclaimer

Use this project only against systems and networks you own or are explicitly authorized to assess. You are solely responsible for complying with all applicable laws, regulations, and engagement scope.

## Requirements

- Python 3.10+
- `nmap`
- `ffuf`
- `ipcalc`
- `iproute2` or equivalent (`ip` command must be available)
- `iputils-ping` or equivalent (`ping` command must be available)
- A supported package manager for automatic dependency installation: `apt` or `yay`
- Root privileges when running the script

## Clone The Project

```bash
git clone https://github.com/daFinndus/reconnoisseur.git
cd reconnoisseur
```

## Basic Usage

Show the built-in help:

```bash
python3 reconnoisseur.py --help
```

Run a basic scan against a single host:

```bash
sudo python3 reconnoisseur.py -t 10.10.0.10
```

Run with a custom ping timeout and verbose logging:

```bash
sudo python3 reconnoisseur.py -t example.com -pt 15 -v
```

Run a full TCP sweep and skip service detection:

```bash
sudo python3 reconnoisseur.py -t 10.10.0.10 -fp -nss
```

Scan a subnet (must be on the same local network):

```bash
sudo python3 reconnoisseur.py -t 10.10.0.0/24
```

Skip all confirmation prompts and specify a project name upfront:

```bash
sudo python3 reconnoisseur.py -t 10.10.0.10 -y -pn my-project
```

## Options

| Flag   | Long form           | Description                                                           |
| ------ | ------------------- | --------------------------------------------------------------------- |
| `-t`   | `--target`          | Target hostname, IPv4 address, or IPv4 CIDR range (required)          |
| `-pt`  | `--pingout`         | Timeout in seconds for the reachability check (default: 10, max: 120) |
| `-fp`  | `--full-ports`      | Scan all 65535 TCP ports instead of the default top 1000              |
| `-nss` | `--no-service-scan` | Skip the follow-up `nmap -sV -sC` service detection scan              |
| `-pn`  | `--project-name`    | Set the project name and skip the interactive naming prompt           |
| `-y`   | `--yes`             | Skip all interactive confirmation prompts                             |
| `-ncc` | `--no-color-check`  | Skip the terminal color support check at startup                      |
| `-nd`  | `--no-delay`        | Disable the brief delays between log messages                         |
| `-v`   | `--verbose`         | Pass `-v` to `nmap` for verbose scan output                           |
| `-h`   | `--help`            | Print usage information and exit                                      |

## Project Structure

```
reconnoisseur.py          Entry point and main workflow
modules/
  config.py               Runtime settings and defaults
  helpers.py              Colored logging functions (step, info, success, warn, error)
  init.py                 Workspace directory setup
  parser.py               CLI argument parsing, input validation, and target reachability
  ports.py                Port scanning, service detection, and subnet host discovery
  system.py               Package manager detection and dependency verification
  target.py               Target format validators for IPv4, hostnames, and CIDR
  web_enumeration.py      Web enumeration (planned)
```

## What The Script Does

1. Displays help when `-h` or `--help` is passed
2. Parses and validates all CLI arguments
3. Optionally displays a color check to confirm terminal output is readable
4. Detects a supported package manager (`apt` or `yay`)
5. Verifies required tools are installed and offers to install any that are missing
6. Validates the target format (hostname, IPv4, or CIDR) and confirms it is reachable via ping
7. For CIDR targets, checks that the host is on the same local subnet before proceeding
8. Prompts for a project name (or uses `-pn`) and creates a workspace under `output/<name>/`
9. For CIDR targets, runs an `nmap -sn` host discovery sweep and iterates over each live host
10. Runs an initial `nmap` port scan (top 1000 or all 65535 TCP ports depending on `-fp`)
11. Runs a follow-up `nmap -sV -sC` scan against discovered open ports unless `-nss` is set

All results are saved to `output/<project-name>/nmap/` in `.nmap`, `.gnmap`, and `.xml` formats.

## Notes

- Subnet scanning (`-t x.x.x.x/24`) requires the host to be on the same local network as the target range
- The `-y` flag suppresses all prompts including workspace overwrite confirmation; use with care
- Package manager support is currently limited to `apt` and `yay`
- The `web-enumeration.sh` module is a stub and not yet functional
