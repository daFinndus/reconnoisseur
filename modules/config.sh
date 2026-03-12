# This file stores all global variables and default values
# --------------------------------------------------------

# This is the targets IP address or subnet to scan
TARGET=""
SUBNET=false

# This is the output directory to put the workspace in
OUTPUT=""

# The project name, relevant for the workspace
PROJECT_NAME=""

# The workspace directory of the project
WORKSPACE=""

# This flag controls script verbosity
VERBOSE=false

# Flags for the various scan types
FULL_PORT_SCAN=false
SERVICE_SCAN=true

# Parameter for ping timeout
PINGOUT=""

# Flags for delay after messages, initial color check, and confirmation prompts
DELAY=true
COLOR_CHECK=true
YES=false

# Default readonly variables
readonly DEFAULT_OUTPUT="output"
readonly DEFAULT_PINGOUT=10
