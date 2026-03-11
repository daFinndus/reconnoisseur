# Reconnoisseur

Reconnoisseur is a Bash-based reconnaissance helper that validates a target, prepares a workspace, checks required tools, and starts an initial port scan.

## Disclaimer

Use this project only against systems and networks you own or are explicitly authorized to assess. You are responsible for complying with applicable laws, rules, and engagement scope.

## Requirements

- Bash
- `nmap`
- `ffuf`
- `ipcalc`
- `iproute2` or equivalent tools that provide `ip`
- `iputils-ping` or equivalent tools that provide `ping`
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
./reconnoisseur.sh --help
```

Run a basic scan against a target:

```bash
sudo ./reconnoisseur.sh -t 10.10.0.10
```

Run with a custom ping timeout and verbose logging:

```bash
sudo ./reconnoisseur.sh -t example.com -pt 15 -v
```

Run a full TCP sweep and skip service detection:

```bash
sudo ./reconnoisseur.sh -t 10.10.0.10 -fp -nss
```

Use custom output and wordlist directories:

```bash
sudo ./reconnoisseur.sh -t 10.10.0.10 -o output -w wordlists
```

## Options

- `-t`, `--target`: Target domain, IPv4 address, or IPv4 CIDR range
- `-pt`, `--pingout`: Timeout in seconds for the reachability check
- `-fp`, `--full-ports`: Scan all TCP ports instead of the default top 1000
- `-nss`, `--no-service-scan`: Skip the follow-up `nmap -sV -sC` scan
- `-v`, `--verbose`: Enable verbose logging
- `-o`, `--output`: Set a custom output directory
- `-w`, `--wordlists`: Set a custom wordlist directory
- `-h`, `--help`: Print the help text and exit

## What The Script Does

1. Shows the help text when requested
2. Checks that the script is run as root
3. Verifies terminal color output
4. Detects a supported package manager
5. Checks for required tools and offers to install missing ones
6. Parses and validates the provided arguments
7. Confirms the target is reachable
8. Creates the workspace structure
9. Runs host discovery for CIDR targets and then scans each live host
10. Runs the initial `nmap` port scan
11. Runs a follow-up `nmap -sV -sC` scan against discovered open ports unless disabled

## Notes

- The script will prompt for a project name before creating the workspace directory
- Dependency installation is interactive when a required tool is missing
- Current package manager support is limited to `apt` and `yay`
- Current target validation supports hostnames, IPv4 addresses, and IPv4 CIDR ranges
- Port scanning is non-interactive; use CLI flags to control full-port and service-scan behavior