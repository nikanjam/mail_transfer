Mail Transfer Tool
A Python-based tool to transfer email accounts and their data between servers running cPanel or DirectAdmin. This script automates the process of extracting email backups, creating email accounts on a destination server, transferring email data, and optionally restoring old passwords.
Features

Supports both cPanel and DirectAdmin control panels for source and destination servers.
Extracts email backups from .tar, .zst, and .tar.zst archives using zstandard and tarfile.
Automatically detects the source and destination control panels.
Transfers email data and updates ownership permissions.
Generates random passwords for new email accounts or restores old passwords from backups.
Logs all actions to /var/log/email_transfer.log for troubleshooting.

Prerequisites

A Linux server with either cPanel or DirectAdmin installed.
Python 3.6+ installed on the system.
uv (a Python package manager) for dependency management (installed via the installer).
Required Python packages: zstandard, tqdm (automatically installed by the script).
Root or sufficient privileges to modify email directories and ownership.

Installation
Using the Installer
The easiest way to get started is by using the provided Bash installer script. It will install uv, download the Python script, and set up the environment.

Download the installer:
wget https://raw.githubusercontent.com/nikanjam/mail_transfer/main/install.sh -O install.sh

Or use the direct link: Download install.sh

Make the script executable:
chmod +x install.sh


Run the installer:
./install.sh



The installer will:

Check for and install uv if it's not already present.
Download mail-transfer.py to your current directory.
Initialize a uv project environment.
Run the script using uv.

Manual Installation
If you prefer to set it up manually:

Clone the repository:git clone https://github.com/nikanjam/mail_transfer.git
cd mail_transfer


Install uv:curl -LsSf https://astral.sh/uv/install.sh | sh


Install dependencies:uv add zstandard tqdm


Run the script:uv run mail-transfer.py



Usage

Ensure you have an email backup file (e.g., .tar, .zst, or .tar.zst).
Run the script:uv run mail-transfer.py


Follow the prompts:
Enter the domain name.
Enter the cPanel or DirectAdmin username.
Provide the path to the backup file.
Confirm the user home directory (/home or /home2).
Optionally restore old passwords when prompted.



Example
$ uv run mail-transfer.py
Enter the domain: example.com
Enter the cPanel/DirectAdmin username: user123
Enter the file path: /path/to/backup.tar.zst
Using user home directory: /home
Detected destination control panel: cPanel
...
Email accounts found: user1, user2
Do you want to restore old passwords? (yes/no): yes

Output

Email accounts and their passwords (if newly generated) are saved to email_passwords.txt.
Logs are written to /var/log/email_transfer.log.

Notes

Ensure you have write permissions to /var/log/ for logging.
The script deletes temporary extraction directories after completion.
For DirectAdmin, you may need to specify a port (default is 2222) when prompted.

Contributing
Feel free to submit issues or pull requests to improve the tool. Suggestions for additional features or bug fixes are welcome!
License
This project is licensed under the MIT License. See the LICENSE file for details.
