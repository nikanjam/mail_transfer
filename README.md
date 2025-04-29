🌟 Mail Transfer Tool
Effortlessly move emails between cPanel and DirectAdmin servers
A slick Python script with a one-shot installer—run it, and you’re good to go!

✨ Why It’s Awesome

🔄 Works with cPanel and DirectAdmin
📦 Unpacks .tar, .zst, and .tar.zst backups
🚚 Transfers emails and fixes permissions automatically
🔑 Generates secure passwords or restores old ones
📜 Logs every step to /var/log/email_transfer.log


🚀 Get Started
One installer does it all—download, setup, and run!

Grab the Installer  
wget https://raw.githubusercontent.com/nikanjam/mail_transfer/main/install.sh -O install.sh


Fire It Up  
bash install.sh



Boom! The installer handles uv, pulls the script, and launches it. Just answer a few quick questions (domain, username, etc.), and you’re set.

⚙️ What You Need

A Linux server with cPanel or DirectAdmin
Root access (or perms to tweak email dirs)


🎉 What You Get

Passwords: Stored in email_passwords.txt (if new)
Logs: Check /var/log/email_transfer.log for details


💡 Join the Fun
Love it? Hate it?  

Drop ideas or bugs in issues  
Send a pull request to make it better!


📜 License
Proudly under the MIT License. Peek at LICENSE for more.
