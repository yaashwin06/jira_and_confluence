# #!/usr/bin/env bash

# echo "============================================"
# echo "   Jira Project Generator - Setup Script"
# echo "============================================"
# echo

# # ---------------------------------------------
# # Helper function
# # ---------------------------------------------
# command_exists() {
#     command -v "$1" >/dev/null 2>&1
# }

# # ---------------------------------------------
# # Check Python installation
# # ---------------------------------------------
# echo "🔍 Checking for Python..."

# if command_exists python3; then
#     PYTHON_BIN=python3
#     echo "✅ Python found: $(python3 --version)"
# else
#     echo "❌ Python3 not found."

#     # macOS installation
#     if [[ "$OSTYPE" == "darwin"* ]]; then
#         echo "➡ Installing Python3 via Homebrew..."
#         if ! command_exists brew; then
#             echo "❌ Homebrew is required but not installed."
#             echo "➡ Install Homebrew first: https://brew.sh/"
#             exit 1
#         fi
#         brew install python
#         PYTHON_BIN=python3

#     # Ubuntu/Debian installation
#     elif [[ -f /etc/debian_version ]]; then
#         echo "➡ Installing Python3 via apt..."
#         sudo apt update
#         sudo apt install -y python3 python3-pip
#         PYTHON_BIN=python3

#     # RHEL/Fedora
#     elif [[ -f /etc/redhat-release ]]; then
#         echo "➡ Installing Python3 via yum/dnf..."
#         sudo dnf install -y python3 python3-pip || sudo yum install -y python3 python3-pip
#         PYTHON_BIN=python3

#     # Unsupported OS
#     else
#         echo "❌ Unsupported OS. Install Python manually."
#         exit 1
#     fi
# fi

# # ---------------------------------------------
# # Check pip installation
# # ---------------------------------------------
# echo
# echo "🔍 Checking for pip..."

# if command_exists pip3; then
#     PIP_BIN=pip3
#     echo "✅ pip found"
# else
#     echo "❌ pip3 not found — installing..."
#     $PYTHON_BIN -m ensurepip --upgrade
#     PIP_BIN="$PYTHON_BIN -m pip"
# fi

# # ---------------------------------------------
# # Install required Python packages
# # ---------------------------------------------
# echo
# echo "📦 Checking Python dependencies..."

# NEEDED_PACKAGES=("requests")

# for pkg in "${NEEDED_PACKAGES[@]}"; do
#     if python3 -c "import $pkg" >/dev/null 2>&1; then
#         echo "   ✔ $pkg already installed"
#     else
#         echo "   ➡ Installing $pkg..."
#         $PIP_BIN install "$pkg"
#     fi
# done

# # ---------------------------------------------
# # Run the Python script
# # ---------------------------------------------
# echo
# echo "🚀 Running Jira Project Generator..."
# echo

# if [[ -f "jira_project_generator.py" ]]; then
#     $PYTHON_BIN jira_project_generator.py
# else
#     echo "❌ ERROR: jira_project_generator.py not found in current directory."
#     echo "Make sure you run this script from the folder containing your Python file."
#     exit 1
# fi

# echo
# echo "✨ Setup complete!"
#!/usr/bin/env bash

# Exit immediately if a command fails
set -e

echo "============================================"
echo "   Jira Project Generator - Setup Script"
echo "============================================"
echo

# ---------------------------------------------
# Helper function
# ---------------------------------------------
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ---------------------------------------------
# Check Python installation
# ---------------------------------------------
echo "🔍 Checking for Python..."

if command_exists python3; then
    PYTHON_BIN=python3
    echo "✅ Python found: $($PYTHON_BIN --version)"
else
    echo "❌ Python3 not found."

    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "➡ Installing Python3 via Homebrew..."
        if ! command_exists brew; then
            echo "❌ Homebrew is required but not installed."
            echo "➡ Install Homebrew first: https://brew.sh/"
            exit 1
        fi
        brew install python
        PYTHON_BIN=python3

    # Debian / Ubuntu
    elif [[ -f /etc/debian_version ]]; then
        echo "➡ Installing Python3 via apt..."
        sudo apt update
        sudo apt install -y python3 python3-pip
        PYTHON_BIN=python3

    # RHEL / Fedora
    elif [[ -f /etc/redhat-release ]]; then
        echo "➡ Installing Python3 via dnf/yum..."
        sudo dnf install -y python3 python3-pip || sudo yum install -y python3 python3-pip
        PYTHON_BIN=python3

    else
        echo "❌ Unsupported OS. Please install Python manually."
        exit 1
    fi
fi

# ---------------------------------------------
# Ensure pip is available
# ---------------------------------------------
echo
echo "🔍 Checking for pip..."

if $PYTHON_BIN -m pip --version >/dev/null 2>&1; then
    echo "✅ pip is available"
else
    echo "❌ pip not found — installing with ensurepip..."
    $PYTHON_BIN -m ensurepip --upgrade
fi

# ---------------------------------------------
# Install required Python packages
# ---------------------------------------------
echo
echo "📦 Installing required Python packages..."

NEEDED_PACKAGES=("requests")

for pkg in "${NEEDED_PACKAGES[@]}"; do
    echo "   ➡ Installing/Upgrading $pkg..."
    $PYTHON_BIN -m pip install --upgrade "$pkg"
done

# ---------------------------------------------
# Run the Python script
# ---------------------------------------------
echo
echo "🚀 Running Jira Project Generator..."
echo

if [[ -f "jira_project_generator.py" ]]; then
    $PYTHON_BIN jira_project_generator.py
else
    echo "❌ ERROR: jira_project_generator.py not found in current directory."
    echo "Make sure you run this script from the folder containing your Python file."
    exit 1
fi

echo
echo "✨ Setup complete!"

