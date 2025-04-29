#!/bin/bash

# Check if uvicorn is installed
if ! command -v uv help run &> /dev/null
then
    echo "uv not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo "uv is already installed."
fi

# Download the Python script
echo "Downloading the script..."
wget https://raw.githubusercontent.com/nikanjam/mail_transfer/main/mail-transfer.py -O mail-transfer.py

# Initialize the directory with uvicorn
echo "Initializing the project with uv..."
uv init

# Run the project with uvicorn
echo "Running the project..."
uv run  mail-transfer.py
