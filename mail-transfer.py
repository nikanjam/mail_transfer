import subprocess
import sys


# insatll package
required_packages = [
    "zstandard",  
    "tqdm",       
]

def install_packages_with_uv(packages):
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Package '{package}' not found. Installing with 'uv add'...")
            result = subprocess.run(["uv", "add", package], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Successfully installed '{package}' with 'uv add'.")
            else:
                print(f"Failed to install '{package}'. Error:\n{result.stderr}")
                sys.exit(1)
        else:
            print(f"Package '{package}' is already installed.")


install_packages_with_uv(required_packages)

import subprocess
import logging
import shutil
import os
import tarfile
import zstandard as zstd
import warnings
import secrets
import string
import sys
from tqdm import tqdm
import random

print("All imports are ready to use.")





#log config
log_file = "/var/log/email_transfer.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


warnings.filterwarnings("ignore", category=RuntimeWarning, module="tarfile")




def install_required_packages():
    try:
        subprocess.run(["uv", "add", "tqdm"], check=True)
        subprocess.run(["uv", "add", "zstandard"], check=True)
        logging.info("Successfully installed tqdm and zstandard.")
    except subprocess.CalledProcessError as e:
        logging.error("Failed to install required packages.", exc_info=True)
        sys.exit(1)


def detect_user_home(user_name):
    home_path = "/home"
    home2_path = "/home2"
    
    if os.path.exists(f"{home_path}/{user_name}"):
        print(f"User '{user_name}' found in /home.")
        confirm = input(f"Is '{home_path}' the correct path? (yes/no): ").strip().lower()
        if confirm == "yes":
            return home_path
    if os.path.exists(f"{home2_path}/{user_name}"):
        print(f"User '{user_name}' found in /home2.")
        confirm = input(f"Is '{home2_path}' the correct path? (yes/no): ").strip().lower()
        if confirm == "yes":
            return home2_path
    
    raise ValueError(f"User '{user_name}' not found in /home or /home2, or path not confirmed.")

#get server ip
def get_server_ip():
    try:
        ip = subprocess.check_output("hostname -I", shell=True, text=True).strip().split()[0]
        logging.info(f"Detected server IP: {ip}")
        return ip
    except Exception as e:
        logging.error("Failed to detect server IP.", exc_info=True)
        raise

def extract_archive(file_path, extract_to):
    if tarfile.is_tarfile(file_path):
        logging.info(f"Opening tar archive {file_path}...")
        with tarfile.open(file_path, 'r:*') as tar:
            members = tar.getmembers()
            with tqdm(total=len(members), desc="Extracting files", unit="file") as pbar:
                for member in members:
                    tar.extract(member, path=extract_to)
                    pbar.update(1)
        logging.info(f"Archive extracted to {extract_to}")
    elif file_path.endswith('.zst'):
        output_tar_path = os.path.join(extract_to, os.path.basename(file_path).replace('.zst', ''))
        total_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as compressed_file:
            with zstd.ZstdDecompressor().stream_reader(compressed_file) as decompressor:
                with open(output_tar_path, 'wb') as out_file:
                    with tqdm(total=total_size, desc="Decompressing .zst", unit="B", unit_scale=True) as pbar:
                        while True:
                            chunk = decompressor.read(16384)
                            if not chunk:
                                break
                            out_file.write(chunk)
                            pbar.update(len(chunk))
        logging.info(f".zst file extracted to {output_tar_path}")

        if tarfile.is_tarfile(output_tar_path):
            with tarfile.open(output_tar_path, 'r:*') as tar:
                members = tar.getmembers()
                with tqdm(total=len(members), desc="Extracting inner tar files", unit="file") as pbar:
                    for member in members:
                        tar.extract(member, path=extract_to)
                        pbar.update(1)
            logging.info(f"Inner tar file extracted to {extract_to}")
            os.remove(output_tar_path)
    elif file_path.endswith('.tar.zst'):
        total_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as compressed_file:
            with zstd.ZstdDecompressor().stream_reader(compressed_file) as decompressor:
                with tarfile.open(fileobj=decompressor, mode='r:*') as tar:
                    members = tar.getmembers()
                    with tqdm(total=len(members), desc="Extracting .tar.zst", unit="file") as pbar:
                        for member in members:
                            tar.extract(member, path=extract_to)
                            pbar.update(1)
        logging.info(f".tar.zst file extracted to {extract_to}")
    else:
        logging.error("Unsupported file format.")
        raise ValueError("Unsupported file format. Only tar.gz, gz, tar.zst, and zst are supported.")

def find_email_accounts(extract_path, domain, control_panel):
    email_accounts = []
    if control_panel == "cpanel":
        email_path = os.path.join(extract_path, 'homedir', 'mail', domain)
    else:  # directadmin
        email_path = os.path.join(extract_path, 'imap', domain)

    if os.path.exists(email_path):
        for entry in os.listdir(email_path):
            entry_path = os.path.join(email_path, entry)
            if os.path.isdir(entry_path):
                email_accounts.append(entry)
    return email_accounts

def detect_destination_control_panel():
    if os.path.exists("/usr/local/cpanel"):
        return "cpanel"
    elif os.path.exists("/usr/local/directadmin"):
        da_port=input("Enter the DirectAdmin port (default is 2222): ").strip()
        if not da_port:
            da_port = "2222"
        if not da_port.isdigit():
            raise ValueError("Invalid port number. Please enter a valid number.")
        return "directadmin"
    
    else:
        raise ValueError("Destination control panel could not be detected. Please ensure cPanel or DirectAdmin is installed.")

def check_control_panel(extract_path):
    homedir_found = False
    imap_found = False
    for root, dirs, files in os.walk(extract_path):
        if 'homedir' in dirs:
            homedir_found = True
        if 'imap' in dirs:
            imap_found = True
        if homedir_found or imap_found:
            break
    return homedir_found, imap_found


def generate_random_password(length=12):
    if length < 4:
        raise ValueError("Password length must be at least 4 to include all character types.")
    
    # Define the allowed character sets
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "_-!^*"
    
    # Ensure at least one character from each category
    lower_char = secrets.choice(lower)
    upper_char = secrets.choice(upper)
    digit_char = secrets.choice(digits)
    symbol_char = secrets.choice(symbols)
    
    # Remaining characters
    remaining_length = length - 4  # Since we already selected 4 characters
    all_chars = lower + upper + digits + symbols
    remaining_chars = [secrets.choice(all_chars) for _ in range(remaining_length)]

    # Combine all characters and shuffle
    password_list = list(lower_char + upper_char + digit_char + symbol_char + ''.join(remaining_chars))
    random.shuffle(password_list)
    
    return ''.join(password_list)

def delete_existing_email_data(user_name, domain, email_account, control_panel_dest , user_home):
    if control_panel_dest == "cpanel":
        email_path = f"{user_home}/{user_name}/mail/{domain}/{email_account}"
    elif control_panel_dest == "directadmin":
        email_path = f"{user_home}/{user_name}/imap/{domain}/{email_account}/Maildir"
    else:
        raise ValueError("Unsupported control panel for deletion.")

    if os.path.exists(email_path):
        shutil.rmtree(email_path)
        logging.info(f"Deleted existing data for {email_account}@{domain}")

def transfer_backup_email_data(extract_to, user_name, domain, email_account, control_panel_source, control_panel_dest , user_home):
    if control_panel_source == "cpanel":
        source_path = os.path.join(extract_to, 'homedir', 'mail', domain, email_account)
    elif control_panel_source == "directadmin":
        source_path = os.path.join(extract_to, 'imap', domain, email_account, 'Maildir')
    else:
        raise ValueError("Unsupported control panel for source backup.")

    if control_panel_dest == "cpanel":
        dest_path = f"{user_home}/{user_name}/mail/{domain}/{email_account}"
    elif control_panel_dest == "directadmin":
        dest_path = f"{user_home}/{user_name}/imap/{domain}/{email_account}/Maildir"
    else:
        raise ValueError("Unsupported control panel for destination.")

    if os.path.exists(source_path):
        shutil.copytree(source_path, dest_path)
        logging.info(f"Transferred backup data for {email_account}@{domain} to destination.")

def update_owner(user_name, domain, control_panel_dest , user_home):
    if control_panel_dest == "cpanel":
        email_base_path = f"{user_home}/{user_name}/mail/{domain}"
        owner = f"{user_name}:{user_name}"
    elif control_panel_dest == "directadmin":
        email_base_path = f"{user_home}/{user_name}/imap/{domain}"
        owner = f"{user_name}:mail"
    else:
        raise ValueError("Unsupported control panel for setting ownership.")

    subprocess.run(['chown', '-R', owner, email_base_path])
    logging.info(f"Ownership updated for {email_base_path} to {owner}")


def create_email_accounts(email_accounts, domain, user_name, control_panel_dest, control_panel_source, extract_to,  user_home , password_file="email_passwords.txt" ):
    if not email_accounts:
        logging.info("No email accounts to create.")
        return

    server_ip = get_server_ip() 
    with open(password_file, 'w') as pf:
        pf.write("Email Account\tPassword\n")
        pf.write("============================\n")
        for email in email_accounts:
            password = generate_random_password()
            try:
               #check dest control
                if control_panel_dest == "directadmin":
                    #get token directadmin
                    raw_api_url = subprocess.check_output(['da', 'api-url', '--user', user_name], text=True).strip()

                    #change nameserver to ip
                    if "https://" in raw_api_url:
                        
                        api_url = raw_api_url[:-(len(raw_api_url.split('@')[1].split(':')[0]) + 6)] + f"@{server_ip}:{da_port}"
                    elif "http://" in raw_api_url:
                        
                        api_url = raw_api_url[:-(len(raw_api_url.split('@')[1].split(':')[0]) + 6)] + f"@{server_ip}:{da_port}"
                    else:
                        logging.error("Invalid API URL format.")
                        continue

                    logging.info(f"Using API URL: {api_url}")

                    #send request to directadmin server
                    payload = f'{{"user":"{email}","domain":"{domain}","passwd2":"{password}","passwd":"{password}","quota":"10000","json":"yes","action":"create"}}'
                    logging.info(f"Sending payload: {payload}")
                    response = subprocess.run(['curl', '--insecure', '--silent', '--write-out', '\n%{http_code}', '--data', payload, f"{api_url}/CMD_EMAIL_POP?json=yes"], capture_output=True, text=True)

                    status_code = response.stdout.splitlines()[-1]
                    if status_code == "200":
                        logging.info(f"Created email: {email}@{domain} via DirectAdmin API")
                        delete_existing_email_data(user_name, domain, email, control_panel_dest , user_home)
                        transfer_backup_email_data(extract_to, user_name, domain, email, control_panel_source, control_panel_dest, user_home)
                        pf.write(f"{email}@{domain}\t{password}\n")
                    else:
                        logging.error(f"Failed to create mailbox. API URL: {api_url}, Response: {response.stdout}")

                elif control_panel_dest == "cpanel":
                    #api for create mail in cpanel
                    logging.info(f"Using cPanel method to create email: {email}@{domain}")
                    command = [
                        "uapi", "--user", user_name, "Email", "add_pop",
                        f"email={email}", f"password={password}", f"quota=10000", f"domain={domain}", "skip_update_db=1"
                    ]
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.returncode == 0:
                        logging.info(f"Created email: {email}@{domain} via cPanel uAPI")
                        delete_existing_email_data(user_name, domain, email, control_panel_dest, user_home)
                        transfer_backup_email_data(extract_to, user_name, domain, email, control_panel_source, control_panel_dest, user_home)
                        pf.write(f"{email}@{domain}\t{password}\n")
                    else:
                        logging.error(f"Failed to create email using cPanel uAPI. Error: {result.stderr}")

            except Exception as ex:
                logging.error(f"Error creating/transferring data for {email}@{domain}.", exc_info=True)


    
    # echo username & domain
    logging.info(f"Operation completed successfully for {user_name} on {domain} ")
    


    update_owner(user_name, domain, control_panel_dest , user_home)
    logging.info(f"Email accounts and their passwords saved to {password_file}")
    #separate Logs
    logging.info("=" * 80)


def restore_old_passwords(email_accounts, domain, user_name, control_panel_source, control_panel_dest, extract_to , user_home):
    try:
        if control_panel_source == "cpanel":
            source_file = os.path.join(extract_to, "homedir", "etc", domain, "shadow")
        elif control_panel_source == "directadmin":
            source_file = os.path.join(extract_to, "backup", domain, "email", "passwd")
        else:
            raise ValueError("Unsupported source control panel.")

        if control_panel_dest == "cpanel":
            dest_file = f"{user_home}/{user_name}/etc/{domain}/shadow"
        elif control_panel_dest == "directadmin":
            dest_file = f"/etc/virtual/{domain}/passwd"
        else:
            raise ValueError("Unsupported destination control panel.")

        # Check if source file exists
        if not os.path.exists(source_file):
            logging.warning(f"Source password file {source_file} not found. Skipping password restoration.")
            return

        # Read source passwords
        source_passwords = {}
        with open(source_file, 'r') as sf:
            for line in sf:
                parts = line.strip().split(':')
                if len(parts) >= 2:
                    username, hashed_password = parts[0], parts[1]
                    source_passwords[username] = hashed_password

        # Read destination file and update passwords
        if not os.path.exists(dest_file):
            logging.warning(f"Destination password file {dest_file} not found. Skipping password restoration.")
            return

        updated_lines = []
        with open(dest_file, 'r') as df:
            for line in df:
                parts = line.strip().split(':')
                if len(parts) >= 2:
                    username = parts[0]
                    if username in source_passwords:
                        parts[1] = source_passwords[username]  # Update the password
                        logging.info(f"Password updated for {username}@{domain}")
                updated_lines.append(':'.join(parts))

        # Write updated lines back to the destination file
        with open(dest_file, 'w') as df:
            df.write('\n'.join(updated_lines) + '\n')

        logging.info(f"Old passwords successfully restored for domain {domain}.")

    except Exception as e:
        logging.error("An error occurred while restoring old passwords.", exc_info=True)

def main():
    install_required_packages()
    domain = input("Enter the domain: ").strip()
    user_name = input("Enter the cPanel/DirectAdmin username: ").strip()
    file_path = input("Enter the file path: ").strip()
    user_home = detect_user_home(user_name)
    print(f"Using user home directory: {user_home}")
    extract_to = f"{user_home}/mail-transfer/{user_name}"


    try:
        control_panel_dest = detect_destination_control_panel()
        logging.info(f"Detected destination control panel: {control_panel_dest}")
    except ValueError as ve:
        logging.error("Control panel detection failed.", exc_info=True)
        sys.exit(1)

    try:
        os.makedirs(extract_to, exist_ok=True)
        extract_archive(file_path, extract_to)

        files_in_extracted = os.listdir(extract_to)
        if len(files_in_extracted) == 1 and os.path.isdir(os.path.join(extract_to, files_in_extracted[0])):
            extract_to = os.path.join(extract_to, files_in_extracted[0])

        homedir_found, imap_found = check_control_panel(extract_to)

        if homedir_found:
            control_panel_source = "cpanel"
            logging.info("Source control panel: cPanel")
        elif imap_found:
            control_panel_source = "directadmin"
            logging.info("Source control panel: DirectAdmin")
        else:
            logging.error("Source control panel could not be detected.")
            raise ValueError("Could not detect the source control panel.")

        email_accounts = find_email_accounts(extract_to, domain, control_panel_source)
        if email_accounts:
            logging.info(f"Email accounts found: {', '.join(email_accounts)}")
            create_email_accounts(email_accounts, domain, user_name, control_panel_dest, control_panel_source, extract_to , user_home)

            
            restore_old_passwords_flag = input("Do you want to restore old passwords? (yes/no): ").strip().lower()
            if restore_old_passwords_flag == "yes":
                 restore_old_passwords(email_accounts, domain, user_name, control_panel_source, control_panel_dest, extract_to , user_home)
    except Exception as e:
        logging.error("An error occurred during execution.", exc_info=True)
        sys.exit(1)

    try:
         #remove extarct file
        shutil.rmtree(extract_to)
        logging.info(f"Successfully deleted the temporary directory: {extract_to}")
    except Exception as e:
        logging.error(f"Failed to delete the directory {extract_to}.", exc_info=True)

if __name__ == "__main__":
    main()

