Mail Transfer Tool
A powerful Python tool to seamlessly transfer email accounts and data between cPanel and DirectAdmin servers.
This script automates the extraction of email backups, creates email accounts on a destination server, transfers email data, and optionally restores old passwords—all with a user-friendly CLI experience.

✨ Features

Cross-Platform Support: Works with both cPanel and DirectAdmin for source and destination servers.
Backup Extraction: Handles .tar, .zst, and .tar.zst archives using zstandard and tarfile.
Auto-Detection: Identifies source and destination control panels automatically.
Data Migration: Transfers email data and updates file ownership permissions.
Password Management: Generates secure random passwords or restores old ones from backups.
Progress Tracking: Uses tqdm for real-time extraction and decompression feedback.
Detailed Logging: Records all actions in /var/log/email_transfer.log.


📋 Prerequisites
Before you begin, ensure you have:

A Linux server with cPanel or DirectAdmin installed.
Python 3.6+ installed on your system.
uv (Python package manager) for dependency management (installed via the installer).
Python packages: zstandard and tqdm (automatically installed).
Root or sufficient privileges to modify email directories and ownership.


🚀 Installation
Option 1: Using the Installer (Recommended)
Get started quickly with our Bash installer, which sets up everything for you.

Download the Installer:
wget https://raw.githubusercontent.com/nikanjam/mail_transfer/main/install.sh -O install.sh

Or grab it here: Download install.sh

Make it Executable:
chmod +x install.sh


Run the Installer:
./install.sh



What it does:

Installs uv if missing.
Downloads mail-transfer.py.
Sets up a uv environment and runs the script.


Option 2: Manual Installation
For more control, set it up manually:

Clone the Repository:
git clone https://github.com/nikanjam/mail_transfer.git
cd mail_transfer


Install uv:
curl -LsSf https://astral.sh/uv/install.sh | sh


Install Dependencies:
uv add zstandard tqdm


Run the Script:
uv run mail-transfer.py




🛠️ Usage

Prepare an email backup file (e.g., .tar, .zst, or .tar.zst).
Launch the script:uv run mail-transfer.py


Follow the interactive prompts:
Enter the domain (e.g., example.com).
Provide the cPanel/DirectAdmin username.
Specify the backup file path.
Confirm the user home directory (/home or /home2).
Choose whether to restore old passwords.



Example Run
$ uv run mail-transfer.py
Enter the domain: example.com
Enter the cPanel/DirectAdmin username: user123
Enter the file path: /path/to/backup.tar.zst
Using user home directory: /home
Detected destination control panel: cPanel
...
Email accounts found: user1, user2
Do you want to restore old passwords? (yes/no): yes


📤 Output

Email Accounts & Passwords: Saved to email_passwords.txt (if newly generated).
Logs: Stored in /var/log/email_transfer.log for debugging.


⚠️ Notes

Ensure write access to /var/log/ for logging.
Temporary extraction directories are cleaned up after completion.
For DirectAdmin, specify a port (default: 2222) if prompted.


🤝 Contributing
We welcome contributions! To get involved:

Fork the repository.
Submit a pull request with your changes.
Report bugs or suggest features via issues.


📜 License
This project is licensed under the MIT License. See the LICENSE file for details.
