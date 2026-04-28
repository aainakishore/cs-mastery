"""
Patch Cloud Devops — Consolidated Patch Script
Consolidated from: patch_linux.py, patch_git.py, patch_docker.py, patch_k8s.py, patch_cicd.py, patch_cloud.py, patch_aws_prac.py, patch_aws_mastery.py, patch_serverless.py, patch_serverless_fix.py, patch_sls_final.py, patch_pycharm.py
Run: python3 scripts/patch_cloud_devops.py
Each section is clearly delimited — you can copy/edit individual sections.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent / "src/content/topics"


def patch(folder, filename, updates):
    p = BASE / folder / filename
    if not p.exists():
        print(f"  SKIP (not found): {folder}/{filename}")
        return
    d = json.loads(p.read_text())
    before_q = len(d.get("questions", []))
    d.update(updates)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print(f"  OK {filename}: guide={len(d.get('guide',''))} q={len(d.get('questions',[]))} fc={len(d.get('flashcards',[]))}")


def main():

    # ── patch_linux.py ──────────────────────────────────────────────────────────────────
    p = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/linux-essentials.json')
    d = json.loads(p.read_text())

    NEW_GUIDE = (
        "# Linux Essentials\n\n"
        "## What Even Is Linux? (Start Here If You Are New)\n\n"
        "Imagine your computer is a restaurant. The **hardware** (CPU, RAM, disk) is the kitchen equipment. "
        "The **operating system** is the head chef who controls everything — decides who gets to use the grills, "
        "hands out ingredients, and keeps order. Linux is one such head chef, and it runs on almost every server, "
        "cloud machine, Docker container, and CI/CD pipeline in the world.\n\n"
        "You have likely used Windows or macOS as your personal computer OS. Linux is different — it was designed "
        "from the ground up for servers, automation, and multi-user environments. It is fast, stable, free, and open "
        "source (anyone can read or modify its code).\n\n"
        "**Why should a developer learn Linux?**\n"
        "- Your code runs on Linux servers (AWS EC2, GCP, Azure — all Linux under the hood)\n"
        "- Docker containers ARE Linux\n"
        "- CI/CD pipelines run bash scripts on Linux runners\n"
        "- SSH into any production machine = you are in a Linux terminal\n"
        "- Kubernetes pods run Linux containers\n\n"
        "```\n"
        "Your laptop (macOS/Windows)\n"
        "        |\n"
        "        | SSH connection\n"
        "        v\n"
        "Linux Server (AWS EC2, GCP VM, VPS...)\n"
        "  - Ubuntu 22.04 LTS  (most popular for servers)\n"
        "  - CentOS / RHEL     (enterprise)\n"
        "  - Alpine Linux      (used inside Docker - tiny 5MB)\n"
        "```\n\n"
        "---\n\n"
        "## The Terminal - Your New Best Friend\n\n"
        "When you work with Linux, you do not click around a graphical UI. You type commands in a **terminal** "
        "(also called shell, command line, or CLI - Command Line Interface).\n\n"
        "**Analogy:** Think of the terminal like texting your computer. Instead of clicking 'New Folder', "
        "you type `mkdir my-folder`. It feels weird at first, but it is 10x faster once you know the language.\n\n"
        "The most common shell is **bash** (Bourne Again Shell). When you open a terminal, you see a prompt:\n\n"
        "```\n"
        "alice@myserver:~$\n"
        "  |       |    | |\n"
        "  |       |    | +-- $ means regular user  (# means root/admin)\n"
        "  |       |    +---- ~ means you are in your home directory\n"
        "  |       +--------- hostname (the server name)\n"
        "  +----------------- your username\n"
        "```\n\n"
        "You type a command, press Enter, see the output, done:\n\n"
        "```bash\n"
        "alice@myserver:~$ echo \"Hello Linux\"\n"
        "Hello Linux\n"
        "alice@myserver:~$        <-- prompt returns, ready for next command\n"
        "```\n\n"
        "---\n\n"
        "## The Filesystem - Everything Is a File\n\n"
        "Linux has one giant directory tree. Everything lives inside it — programs, configs, logs, "
        "even hardware devices. This is different from Windows which has C:\\ D:\\ etc.\n\n"
        "```\n"
        "/                          <- the root - the very top of everything\n"
        "|\n"
        "+-- bin/                   <- essential programs: ls, cp, mv, echo\n"
        "+-- etc/                   <- ALL configuration files live here\n"
        "|   +-- nginx/\n"
        "|   |   +-- nginx.conf     <- Nginx web server config\n"
        "|   +-- ssh/\n"
        "|   |   +-- sshd_config    <- SSH server settings\n"
        "|   +-- hosts              <- hostname to IP mappings\n"
        "+-- home/                  <- user home directories\n"
        "|   +-- alice/             <- alice personal space (written as ~)\n"
        "|   +-- bob/\n"
        "+-- var/                   <- data that changes over time\n"
        "|   +-- log/               <- LOG FILES live here!\n"
        "|       +-- syslog         <- system-wide events\n"
        "|       +-- auth.log       <- login attempts\n"
        "|       +-- nginx/access.log  <- every HTTP request\n"
        "+-- tmp/                   <- temporary files - WIPED on reboot\n"
        "+-- usr/                   <- user-installed programs\n"
        "|   +-- bin/               <- programs installed via apt\n"
        "+-- proc/                  <- VIRTUAL: shows running processes as files\n"
        "+-- dev/                   <- device files (disks, terminals)\n"
        "    +-- sda                <- your primary hard drive\n"
        "```\n\n"
        "**Memory trick - what each folder means:**\n"
        "- `/etc` = The HR / Policy office (all the rules and configs)\n"
        "- `/var/log` = The security camera room (audit logs)\n"
        "- `/home/alice` = Alice's personal office\n"
        "- `/tmp` = A whiteboard erased every morning\n"
        "- `/usr/bin` = Where all the installed software tools live\n"
        "- `/proc` = A live snapshot of what the system is doing RIGHT NOW\n\n"
        "**Real-world scenario:** Your Spring Boot app crashes at 3am. You SSH in and:\n"
        "1. Go to `/var/log/` to find your app log file\n"
        "2. Run `tail -100 /var/log/myapp/app.log` to see the last 100 lines\n"
        "3. Spot the `OutOfMemoryError`, understand it, fix the heap setting\n\n"
        "---\n\n"
        "## Navigating the Filesystem - Moving Around\n\n"
        "These are the commands you will type hundreds of times per day:\n\n"
        "```bash\n"
        "# WHERE AM I RIGHT NOW?\n"
        "pwd\n"
        "# Output: /home/alice\n"
        "# pwd = Print Working Directory\n\n"
        "# WHAT IS IN THIS FOLDER?\n"
        "ls              # basic list\n"
        "ls -l           # long format: shows permissions, size, date\n"
        "ls -a           # show hidden files too (files starting with .)\n"
        "ls -lah         # everything: long + all + human-readable sizes\n"
        "# Example output:\n"
        "# drwxr-xr-x  3 alice alice 4.0K Jan 15 09:00 projects/\n"
        "# -rw-r--r--  1 alice alice  82K Jan 14 18:30 notes.txt\n"
        "# d = directory, - = regular file\n\n"
        "# MOVE TO A DIFFERENT FOLDER\n"
        "cd /etc                # go to /etc  (absolute path - starts from /)\n"
        "cd projects            # go to projects/ folder (relative - from where you are)\n"
        "cd ..                  # go up one level (like clicking back)\n"
        "cd ~                   # go to YOUR home directory\n"
        "cd -                   # go back to where you just were\n\n"
        "# CREATE FOLDERS AND FILES\n"
        "mkdir photos           # make a new folder\n"
        "mkdir -p a/b/c/d       # make nested folders all at once\n"
        "touch notes.txt        # create empty file\n\n"
        "# COPY, MOVE, RENAME, DELETE\n"
        "cp file.txt backup.txt        # copy a file\n"
        "cp -r folder/ backup_folder/  # copy a folder (need -r for recursive)\n"
        "mv old.txt new.txt            # rename a file\n"
        "mv file.txt /tmp/             # move file to /tmp folder\n"
        "rm file.txt                   # delete a file (NO RECYCLE BIN!)\n"
        "rm -rf folder/                # delete folder and EVERYTHING inside\n"
        "```\n\n"
        "> WARNING: `rm -rf` has no undo. There is no trash. Always double-check before running it.\n\n"
        "---\n\n"
        "## Reading Files - Viewing Content\n\n"
        "```bash\n"
        "cat file.txt          # print the whole file on screen\n"
        "less file.txt         # page through (q to quit, arrow keys to scroll, / to search)\n"
        "head -20 file.txt     # show first 20 lines only\n"
        "tail -20 file.txt     # show last 20 lines only\n"
        "tail -f app.log       # LIVE VIEW - shows new lines as they appear\n"
        "                      # perfect for watching logs in real time! Ctrl+C to stop\n\n"
        "# SEARCH INSIDE FILES\n"
        "grep \"ERROR\" app.log               # find lines containing ERROR\n"
        "grep -i \"error\" app.log            # same but case-insensitive\n"
        "grep -r \"database\" /etc/           # search inside ALL files in /etc\n"
        "grep -n \"NullPointer\" app.log      # show line numbers with matches\n"
        "grep -A 3 -B 3 \"FATAL\" app.log     # show 3 lines before and after each match\n"
        "grep -c \"ERROR\" app.log            # just count how many lines match\n"
        "```\n\n"
        "**Real-world scenario:** App is throwing errors in production. You run:\n"
        "```bash\n"
        "tail -f /var/log/myapp/app.log | grep ERROR\n"
        "```\n"
        "This pipes tail into grep - you see ONLY error lines as they appear, live. "
        "You can spot patterns instantly.\n\n"
        "---\n\n"
        "## File Permissions - Who Can Do What\n\n"
        "Every single file in Linux has **access rules** for three groups of people. "
        "This matters a LOT in production - wrong permissions = app crashes or security holes.\n\n"
        "```\n"
        "-rw-r--r--  1  alice  developers  4096  Jan 15  report.txt\n"
        "|          |   |      |\n"
        "|          |   |      +- group name (developers)\n"
        "|          |   +-------- owner name (alice)\n"
        "|          +------------ number of hard links\n"
        "+----------------------- permission string (10 characters)\n"
        "```\n\n"
        "**The 10-character permission string explained:**\n"
        "```\n"
        "  -  r w -  r - -  r - -\n"
        "  |  |   |  |   |  |   |\n"
        "  |  +---+  +---+  +---+\n"
        "  |  owner  group  others\n"
        "  |\n"
        "  + file type: - = regular file\n"
        "               d = directory\n"
        "               l = symbolic link (shortcut)\n"
        "```\n\n"
        "**What r, w, x mean:**\n"
        "```\n"
        "r = read    = can you open and read this file?       (value = 4)\n"
        "w = write   = can you change or delete this file?   (value = 2)\n"
        "x = execute = can you run this as a program?        (value = 1)\n"
        "- = no permission for this slot\n"
        "```\n\n"
        "**How the numbers work in chmod:**\n"
        "```\n"
        "You add up the values to get one number per group:\n\n"
        "rwx = 4+2+1 = 7   (full access)\n"
        "rw- = 4+2+0 = 6   (read + write, no execute)\n"
        "r-x = 4+0+1 = 5   (read + execute, no write)\n"
        "r-- = 4+0+0 = 4   (read only)\n"
        "--- = 0+0+0 = 0   (no access whatsoever)\n\n"
        "chmod 755 script.sh\n"
        "       |||\n"
        "       ||+-- others: 5 = r-x (can read and run, cannot write)\n"
        "       |+--- group:  5 = r-x\n"
        "       +---- owner:  7 = rwx (full access)\n\n"
        "chmod 600 private_key\n"
        "       |||\n"
        "       ||+-- others: 0 = --- (NO access at all)\n"
        "       |+--- group:  0 = --- (NO access at all)\n"
        "       +---- owner:  6 = rw- (can read and write)\n"
        "```\n\n"
        "**Common permission recipes to memorize:**\n"
        "```bash\n"
        "chmod 755 script.sh        # shell scripts: owner full, everyone can read+run\n"
        "chmod 644 config.txt       # config files: owner can edit, everyone can read\n"
        "chmod 600 ~/.ssh/id_rsa    # SSH private key: ONLY owner reads (SSH refuses if wrong!)\n"
        "chmod 700 ~/.ssh/          # .ssh folder: only owner can enter\n"
        "chmod +x deploy.sh         # add execute for everyone (keeps other permissions)\n"
        "chmod -R 755 /var/www/     # -R = recursive: apply to all files inside\n"
        "```\n\n"
        "**chown - change who owns a file:**\n"
        "```bash\n"
        "chown alice report.txt              # change owner to alice\n"
        "chown alice:developers report.txt   # change owner AND group\n"
        "sudo chown -R www-data /var/www/html  # recursive ownership change\n"
        "```\n\n"
        "**Real-world pitfall:** Your app cannot write to its log folder:\n"
        "```bash\n"
        "ls -la /var/log/\n"
        "# drwxr-xr-x  2  root  root  4096  Jan 15  myapp/\n"
        "# Problem: folder is owned by root! Your app user cannot write to it.\n"
        "# Fix:\n"
        "sudo chown -R myappuser:myappuser /var/log/myapp/\n"
        "```\n\n"
        "---\n\n"
        "## Processes - Running Programs\n\n"
        "When you run a program, the OS creates a **process** - an instance of the program "
        "with its own chunk of memory and a unique **PID** (Process ID - just a number).\n\n"
        "```\n"
        "You type: java -jar app.jar\n"
        "                |\n"
        "                v\n"
        "Kernel creates a process:\n"
        "  PID:    4521\n"
        "  Memory: 512MB heap allocated\n"
        "  Files:  opens app.jar, log file, network sockets\n"
        "  CPU:    scheduled to run on available core\n"
        "                |\n"
        "                v\n"
        "Process runs until:\n"
        "  - Normal exit   (code calls System.exit(0))\n"
        "  - Error crash   (unhandled exception)\n"
        "  - You kill it   (SIGTERM or SIGKILL)\n"
        "```\n\n"
        "**Viewing processes:**\n"
        "```bash\n"
        "ps aux\n"
        "# Shows ALL running processes\n"
        "# a=all users  u=user-friendly format  x=include background\n"
        "# Output:\n"
        "# USER   PID  %CPU  %MEM  COMMAND\n"
        "# alice  4521  25.3  12.8  java -jar app.jar\n"
        "# root    234   0.1   0.2  nginx: master process\n\n"
        "top           # live updating process viewer (like Windows Task Manager)\n"
        "htop          # prettier version of top (install: sudo apt install htop)\n"
        "              # q to quit\n\n"
        "pgrep nginx   # find the PID of process named nginx\n"
        "pgrep -a java # find all java processes with their full command\n"
        "```\n\n"
        "**Stopping processes:**\n"
        "```bash\n"
        "kill 4521       # send SIGTERM - politely ask the process to stop\n"
        "kill -9 4521    # send SIGKILL - immediate force kill (no cleanup)\n"
        "killall java    # kill ALL processes named java\n\n"
        "# ALWAYS try SIGTERM first!\n"
        "# SIGTERM = like asking a chef to finish the dish before going home\n"
        "# SIGKILL = like cutting the power - no chance to save anything\n"
        "```\n\n"
        "**Running in background:**\n"
        "```bash\n"
        "./long_script.sh &    # & = run in background, get prompt back immediately\n"
        "nohup ./server.sh &   # nohup = keep running even after terminal closes\n"
        "jobs                  # list background jobs in this terminal\n"
        "fg %1                 # bring job 1 to foreground\n"
        "Ctrl+Z                # pause/suspend current program\n"
        "Ctrl+C                # stop/kill current program\n"
        "```\n\n"
        "---\n\n"
        "## Pipes and Redirection - The Unix Superpower\n\n"
        "This is where Linux becomes incredibly powerful. You can **chain commands together** — "
        "the output of one command becomes the input of the next. It is like an assembly line.\n\n"
        "```\n"
        "command1  |  command2  |  command3\n"
        "    |            |            |\n"
        "    |      takes command1     |\n"
        "    |      output as input    +-- takes command2 output as input\n"
        "    +-- runs first, produces output\n"
        "```\n\n"
        "**Examples:**\n"
        "```bash\n"
        "# Count ERROR lines in a log file\n"
        "grep 'ERROR' app.log | wc -l\n\n"
        "# Find top 10 IPs making POST requests\n"
        "cat access.log | grep 'POST' | awk '{print $1}' | sort | uniq -c | sort -rn | head -10\n"
        "#     |               |               |            |        |           |          |\n"
        "#  read file      keep POSTs    get 1st column  sort   count     sort by count  top 10\n\n"
        "# Find all java processes and show only their PIDs\n"
        "ps aux | grep java | awk '{print $2}'\n"
        "```\n\n"
        "**Redirection - sending output to files instead of screen:**\n"
        "```bash\n"
        "ls -la > filelist.txt        # > OVERWRITES the file (creates if not exists)\n"
        "ls -la >> filelist.txt       # >> APPENDS to end of file\n"
        "cat nope.txt 2> errors.txt   # 2> redirects only ERROR output\n"
        "java -jar app.jar > app.log 2>&1  # both normal AND error output to one file\n"
        "                                   # 2>&1 means 'send stderr to wherever stdout goes'\n\n"
        "# Useful pattern: run app in background, log everything:\n"
        "nohup java -jar app.jar > app.log 2>&1 &\n"
        "```\n\n"
        "---\n\n"
        "## SSH - Connecting to Remote Servers\n\n"
        "SSH (Secure Shell) lets you control a remote Linux server as if you are sitting at it. "
        "All traffic is encrypted - nobody can snoop on your commands.\n\n"
        "```\n"
        "Your Laptop                      Remote Server\n"
        "    |                                 |\n"
        "    |  === encrypted SSH tunnel ===>  |\n"
        "    |                           you control it\n"
        "    |                           run commands\n"
        "    |                           read files\n"
        "    |                           restart services\n"
        "```\n\n"
        "**Connecting to a server:**\n"
        "```bash\n"
        "ssh alice@192.168.1.50           # connect by IP address\n"
        "ssh alice@myserver.com           # connect by hostname\n"
        "ssh -p 2222 alice@server.com     # use port 2222 (default is 22)\n"
        "ssh -i ~/.ssh/mykey.pem ec2-user@3.14.159.26  # AWS EC2 with key file\n"
        "```\n\n"
        "**SSH Key Authentication (better than passwords):**\n"
        "```bash\n"
        "# STEP 1: Generate a key pair on YOUR OWN machine\n"
        "ssh-keygen -t ed25519 -C \"my work laptop key\"\n"
        "# This creates TWO files:\n"
        "#   ~/.ssh/id_ed25519      <- PRIVATE KEY (never share this, ever!)\n"
        "#   ~/.ssh/id_ed25519.pub  <- PUBLIC KEY  (safe to give to servers)\n\n"
        "# STEP 2: Put your public key on the server\n"
        "ssh-copy-id alice@192.168.1.50\n"
        "# Or manually append to server's ~/.ssh/authorized_keys\n\n"
        "# STEP 3: Connect without password!\n"
        "ssh alice@192.168.1.50\n"
        "```\n\n"
        "**How it works (simplified):**\n"
        "```\n"
        "Your public key  ---> goes to the server  (like a padlock)\n"
        "Your private key ---> stays on your laptop (like the key)\n\n"
        "Server says: \"Prove you have the key for this padlock\"\n"
        "Your laptop signs a challenge with private key, sends the signature\n"
        "Server checks the signature with public key\n"
        "Server: \"Valid! Come in.\"\n"
        "You never send the private key over the network!\n"
        "```\n\n"
        "**Copying files over SSH:**\n"
        "```bash\n"
        "scp report.txt alice@server:/home/alice/      # copy TO server\n"
        "scp alice@server:/var/log/app.log ./          # copy FROM server\n"
        "scp -r ./project alice@server:/home/alice/   # copy entire folder\n"
        "```\n\n"
        "**Common SSH problem - Permission denied (publickey):**\n"
        "```\n"
        "Fix checklist:\n"
        "1. chmod 600 ~/.ssh/id_ed25519       (private key must be owner-only)\n"
        "2. chmod 700 ~/.ssh/                 (.ssh folder must be owner-only)\n"
        "3. Check public key is in server ~/.ssh/authorized_keys\n"
        "4. Use correct username (ec2-user for AWS, ubuntu for Ubuntu AMIs)\n"
        "5. Verify server IP/hostname is correct\n"
        "6. Check SSH service: sudo systemctl status ssh\n"
        "```\n\n"
        "---\n\n"
        "## Package Management - Installing Software\n\n"
        "In Linux you do not download installers from websites. "
        "You use a **package manager** - a built-in tool that downloads, installs, and updates software safely.\n\n"
        "**Ubuntu/Debian (apt):**\n"
        "```bash\n"
        "sudo apt update              # first: refresh what packages are available\n"
        "sudo apt install nginx       # install nginx web server\n"
        "sudo apt install -y openjdk-17-jdk  # -y = yes to all prompts\n"
        "sudo apt remove nginx        # uninstall\n"
        "sudo apt upgrade             # upgrade all installed packages\n"
        "apt search \"text editor\"    # search for packages\n"
        "apt show nginx               # get details about a package\n"
        "```\n\n"
        "**CentOS / RHEL / Fedora (dnf):**\n"
        "```bash\n"
        "sudo dnf update\n"
        "sudo dnf install nginx\n"
        "sudo dnf remove nginx\n"
        "```\n\n"
        "**What is sudo?**\n"
        "Most system commands need **root** (admin) privileges. "
        "`sudo` runs that ONE command as root, then drops back:\n"
        "```bash\n"
        "sudo apt install nginx    # runs apt install as root (asks your password)\n"
        "sudo systemctl restart nginx\n"
        "sudo nano /etc/nginx/nginx.conf  # edit a protected config file\n"
        "```\n\n"
        "---\n\n"
        "## Environment Variables - Configuring Programs\n\n"
        "Environment variables are **name=value** settings that programs can read. "
        "This is how you pass database URLs, API keys, and config to your app without hardcoding.\n\n"
        "```bash\n"
        "env                    # see ALL environment variables\n"
        "echo $HOME             # /home/alice\n"
        "echo $USER             # alice\n"
        "echo $PATH             # /usr/local/bin:/usr/bin:/bin\n\n"
        "# Set for current session only\n"
        "export DB_URL=\"postgresql://localhost:5432/mydb\"\n\n"
        "# Set permanently (survives terminal restarts)\n"
        "echo 'export DB_URL=\"postgresql://localhost:5432/mydb\"' >> ~/.bashrc\n"
        "source ~/.bashrc       # reload - makes it active NOW\n"
        "```\n\n"
        "**How PATH works:**\n"
        "```\n"
        "PATH=/usr/local/bin:/usr/bin:/bin\n"
        "          |              |      |\n"
        "          |              |      +-- check /bin/ for the command\n"
        "          |              +--------- check /usr/bin/ next\n"
        "          +------------------------ check /usr/local/bin/ FIRST\n\n"
        "When you type: java\n"
        "Linux searches each PATH folder left-to-right until it finds 'java'\n"
        "If not found: 'command not found' error\n\n"
        "Fix: if java is at /opt/java/bin/java, add to PATH:\n"
        "export PATH=$PATH:/opt/java/bin\n"
        "```\n\n"
        "---\n\n"
        "## System Health - Monitoring Your Server\n\n"
        "```bash\n"
        "# DISK SPACE\n"
        "df -h         # disk free - shows all filesystems with human-readable sizes\n"
        "# Output:\n"
        "# Filesystem   Size   Used  Avail  Use%  Mounted on\n"
        "# /dev/sda1     50G    23G    25G   48%  /\n"
        "du -sh /var/log/   # disk usage of a specific folder\n"
        "du -sh /*          # disk usage of all top-level folders\n\n"
        "# RAM\n"
        "free -h       # show memory usage\n"
        "# Output:\n"
        "#             total   used   free   available\n"
        "# Mem:         15Gi   8Gi    2Gi    6Gi\n\n"
        "# UPTIME AND LOAD\n"
        "uptime        # how long system has been running + load averages\n\n"
        "# HARDWARE INFO\n"
        "lscpu         # CPU info (cores, speed, architecture)\n"
        "ip addr       # network interfaces and IP addresses\n"
        "cat /etc/os-release   # what distro and version is this?\n"
        "uname -a      # kernel version\n"
        "```\n\n"
        "---\n\n"
        "## Editing Text Files\n\n"
        "```bash\n"
        "# NANO - beginner friendly editor\n"
        "nano /etc/hosts\n"
        "# Ctrl+O = save file\n"
        "# Ctrl+X = exit\n"
        "# Ctrl+W = search\n"
        "# Bottom bar shows all shortcuts in plain English\n\n"
        "# VIM - powerful but needs learning\n"
        "vim /etc/nginx/nginx.conf\n"
        "# Press i = enter INSERT mode (now you can type)\n"
        "# Press Esc = back to command mode\n"
        "# Type :wq = save and quit\n"
        "# Type :q! = quit WITHOUT saving (emergency exit!)\n"
        "# Type /word = search for word\n\n"
        "# QUICK EDITS without opening editor\n"
        "sed -i 's/old/new/g' config.txt     # replace 'old' with 'new' in file\n"
        "echo \"new line\" >> config.txt       # append a line to end of file\n"
        "```\n\n"
        "---\n\n"
        "## Mind Map - The Big Picture\n\n"
        "```\n"
        "LINUX ESSENTIALS\n"
        "|\n"
        "+-- FILESYSTEM\n"
        "|   +-- / is root of everything\n"
        "|   +-- /etc = configs\n"
        "|   +-- /var/log = log files\n"
        "|   +-- /home/user = your space\n"
        "|   +-- /tmp = temp (wiped on reboot)\n"
        "|   +-- /proc = virtual (live process info)\n"
        "|\n"
        "+-- NAVIGATION\n"
        "|   +-- pwd (where am I?)\n"
        "|   +-- ls (what is here?)\n"
        "|   +-- cd (move around)\n"
        "|   +-- mkdir, touch, cp, mv, rm\n"
        "|\n"
        "+-- READING FILES\n"
        "|   +-- cat (dump to screen)\n"
        "|   +-- less (scroll through)\n"
        "|   +-- tail -f (live follow)\n"
        "|   +-- grep (search inside)\n"
        "|\n"
        "+-- PERMISSIONS\n"
        "|   +-- rwx = read/write/execute\n"
        "|   +-- 3 groups: owner, group, others\n"
        "|   +-- chmod (change permissions)\n"
        "|   +-- chown (change owner)\n"
        "|   +-- Key recipes: 600=private, 755=script\n"
        "|\n"
        "+-- PROCESSES\n"
        "|   +-- ps aux (see all)\n"
        "|   +-- top/htop (live monitor)\n"
        "|   +-- kill PID (SIGTERM = graceful)\n"
        "|   +-- kill -9 PID (SIGKILL = force)\n"
        "|   +-- & and nohup (background)\n"
        "|\n"
        "+-- PIPES & REDIRECTION\n"
        "|   +-- | (pipe: chain commands)\n"
        "|   +-- > (overwrite to file)\n"
        "|   +-- >> (append to file)\n"
        "|   +-- 2>&1 (merge errors into output)\n"
        "|\n"
        "+-- SSH\n"
        "|   +-- ssh user@host (connect)\n"
        "|   +-- ssh-keygen (generate key pair)\n"
        "|   +-- chmod 600 private key!\n"
        "|   +-- scp (copy files over SSH)\n"
        "|\n"
        "+-- PACKAGES\n"
        "    +-- apt update (refresh list)\n"
        "    +-- apt install X (install)\n"
        "    +-- sudo prefix for admin commands\n"
        "```\n\n"
        "---\n\n"
        "## How This Connects to Other Topics\n\n"
        "- **Git**: You run `git` commands from bash. Every `git push` is a Linux command.\n"
        "- **Docker**: Containers ARE Linux. `docker exec -it container bash` drops you into a Linux shell.\n"
        "- **CI/CD Pipelines**: Pipeline steps are bash scripts on Linux runners.\n"
        "- **Kubernetes**: `kubectl exec -it pod -- bash` gives you a Linux shell inside a pod.\n"
        "- **AWS/Cloud**: EC2 instances are Linux VMs. You SSH in, manage processes, tail logs.\n\n"
        "---\n\n"
        "## Common Beginner Mistakes\n\n"
        "1. **Forgetting sudo** — `Permission denied`? Add `sudo` in front.\n"
        "2. **rm -rf wrong path** — Always `ls` first to confirm what is there before deleting.\n"
        "3. **File not writable** — `ls -la` to check permissions before editing.\n"
        "4. **SSH Permission denied** — Check: `chmod 600 ~/.ssh/id_rsa`, correct username, key in authorized_keys.\n"
        "5. **Command not found** — Program installed but not in PATH. Use `which programname` to find it.\n"
        "6. **Lost in directories** — Run `pwd` to see where you are. `cd ~` always gets you home.\n"
        "7. **grep finds nothing** — Try `grep -i` for case-insensitive. The case might not match.\n\n"
        "---\n\n"
        "## References and Further Learning\n\n"
        "### Videos (Watch These!)\n"
        "- **Linux Command Line Full Course** by tutorialinux: https://www.youtube.com/watch?v=ZtqBQ68cfJc\n"
        "  - 5-hour beginner to intermediate. Go at your own pace.\n"
        "- **60 Linux Commands you NEED to know** by NetworkChuck: https://www.youtube.com/watch?v=gd7BXuUQ91w\n"
        "  - Fast-paced, practical, fun. Great overview.\n\n"
        "### Free Books and Articles\n"
        "- **The Linux Command Line** (free full book): https://linuxcommand.org/tlcl.php\n"
        "  - Best free beginner book by William Shotts. Read chapters 1-10 first.\n"
        "- **Linux Journey** (interactive exercises): https://linuxjourney.com/\n"
        "  - Gamified step-by-step lessons. Do 15 min per day.\n"
        "- **Explain Shell** (paste any command, get it explained): https://explainshell.com/\n"
        "  - Paste `find /var -name '*.log' -mtime -1` and see every part explained visually.\n\n"
        "### Diagrams and Cheatsheets\n"
        "- **Linux Filesystem Hierarchy Diagram**: search 'Linux FHS diagram' on Google Images\n"
        "- **chmod calculator** (visual permissions tool): https://chmod-calculator.com/\n"
        "- **Bash reference manual**: https://www.gnu.org/software/bash/manual/bash.html\n\n"
        "### Practice (hands-on is the only way)\n"
        "- **OverTheWire Bandit** (gamified Linux challenges from zero): https://overthewire.org/wargames/bandit/\n"
        "  - Level 0 starts with just `ssh`. By level 30 you know Linux well.\n"
        "- **TryHackMe Linux Fundamentals** (browser terminal, no install needed): https://tryhackme.com/module/linux-fundamentals\n"
    )

    d['guide'] = NEW_GUIDE
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"Done! Guide length: {len(NEW_GUIDE)} chars")
    print(f"Questions: {len(d['questions'])}, Flashcards: {len(d['flashcards'])}")

    # ── patch_git.py ──────────────────────────────────────────────────────────────────
    p = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/git-fundamentals.json')
    d = json.loads(p.read_text())

    lines = []

    lines.append("# Git Fundamentals")
    lines.append("")
    lines.append("## What Even Is Git? (No Prior Knowledge Assumed)")
    lines.append("")
    lines.append("Imagine you are writing a long essay and you save it as `essay.docx`.")
    lines.append("Then you make changes and save again. Now you want to go back to yesterday's version —")
    lines.append("but you only have one file. You are stuck.")
    lines.append("")
    lines.append("Now imagine every time you save, you take a **snapshot** of the entire project,")
    lines.append("label it with a message like 'added introduction', and can jump back to ANY")
    lines.append("previous snapshot at any time. That is exactly what Git does.")
    lines.append("")
    lines.append("Git is a **version control system** — software that tracks every change you make")
    lines.append("to your code files, so you can:")
    lines.append("- Go back to any previous version")
    lines.append("- See exactly what changed and who changed it")
    lines.append("- Work on new features without breaking the working version")
    lines.append("- Collaborate with a team without overwriting each other's work")
    lines.append("")
    lines.append("**Git vs GitHub — they are NOT the same thing:**")
    lines.append("```")
    lines.append("Git     = the tool on your computer that tracks changes")
    lines.append("GitHub  = a website that hosts your Git repositories online")
    lines.append("          (like Google Drive, but for code with Git superpowers)")
    lines.append("")
    lines.append("Other hosting sites: GitLab, Bitbucket — all use Git underneath")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Installing Git and First-Time Setup")
    lines.append("")
    lines.append("```bash")
    lines.append("# Check if Git is already installed")
    lines.append("git --version")
    lines.append("# Output: git version 2.43.0")
    lines.append("")
    lines.append("# Install on Ubuntu/Debian")
    lines.append("sudo apt install git")
    lines.append("")
    lines.append("# Install on macOS")
    lines.append("brew install git")
    lines.append("")
    lines.append("# REQUIRED: tell Git who you are (stored in every commit)")
    lines.append('git config --global user.name "Alice Smith"')
    lines.append('git config --global user.email "alice@example.com"')
    lines.append("")
    lines.append("# Set VS Code as default editor (optional but nice)")
    lines.append('git config --global core.editor "code --wait"')
    lines.append("")
    lines.append("# See all your config")
    lines.append("git config --list")
    lines.append("```")
    lines.append("")
    lines.append("Why set name and email? Every commit you make gets stamped with this info.")
    lines.append("Your teammates see 'Alice Smith committed: fixed login bug' — not just a random hash.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## The Three Areas — The Most Important Mental Model")
    lines.append("")
    lines.append("Git manages your project through three distinct areas. Understanding this")
    lines.append("eliminates 80% of Git confusion.")
    lines.append("")
    lines.append("```")
    lines.append("  WORKING TREE          STAGING AREA           REPOSITORY")
    lines.append("  (your files)          (the index)            (.git folder)")
    lines.append("")
    lines.append("  what you see          what you are           permanent")
    lines.append("  and edit today        about to commit        history")
    lines.append("")
    lines.append("  essay.txt             [essay.txt v2]         commit abc123")
    lines.append("  style.css             [style.css v3]         commit def456")
    lines.append("  app.js                                       commit ghi789")
    lines.append("")
    lines.append("     |                       |                       |")
    lines.append("     |------ git add ------->|                       |")
    lines.append("     |                       |--- git commit ------->|")
    lines.append("     |<------ git restore ---|                       |")
    lines.append("     |<------ git checkout ---------------------------")
    lines.append("```")
    lines.append("")
    lines.append("**Analogy — the photographer:**")
    lines.append("- **Working Tree** = the scene in front of you (messy, in progress)")
    lines.append("- **Staging Area** = you are choosing which subjects to include in the photo")
    lines.append("- **Repository** = the photo album (permanent snapshots, never deleted)")
    lines.append("")
    lines.append("You stage only the changes relevant to one logical unit of work,")
    lines.append("then commit them. This gives you a clean, meaningful history.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Your First Repository — Step by Step")
    lines.append("")
    lines.append("```bash")
    lines.append("# OPTION A: Start fresh")
    lines.append("mkdir my-project")
    lines.append("cd my-project")
    lines.append("git init")
    lines.append("# Git creates a hidden .git/ folder — this IS the repository")
    lines.append("# Output: Initialized empty Git repository in /my-project/.git/")
    lines.append("")
    lines.append("# OPTION B: Download an existing project from GitHub")
    lines.append("git clone https://github.com/someuser/some-repo.git")
    lines.append("cd some-repo")
    lines.append("# You now have a full copy with all history")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## The Core Daily Workflow")
    lines.append("")
    lines.append("This is what you will do dozens of times per day:")
    lines.append("")
    lines.append("```bash")
    lines.append("# STEP 1: Check what is going on")
    lines.append("git status")
    lines.append("# Shows:")
    lines.append("# - Which files changed (red = unstaged, green = staged)")
    lines.append("# - Which files are new (untracked)")
    lines.append("# - Which branch you are on")
    lines.append("")
    lines.append("# STEP 2: See the actual changes (the diff)")
    lines.append("git diff             # unstaged changes (working tree vs staging area)")
    lines.append("git diff --staged    # staged changes (staging area vs last commit)")
    lines.append("")
    lines.append("# STEP 3: Stage the changes you want to commit")
    lines.append("git add filename.txt    # stage one specific file")
    lines.append("git add src/           # stage everything inside src/ folder")
    lines.append("git add .              # stage EVERYTHING changed in this directory")
    lines.append("git add -p             # interactive: stage specific chunks/lines (powerful!)")
    lines.append("")
    lines.append("# STEP 4: Commit with a clear message")
    lines.append('git commit -m "feat: add user login endpoint"')
    lines.append("# The message is permanent — make it descriptive!")
    lines.append("")
    lines.append("# STEP 5: Push to remote (GitHub/GitLab/etc.)")
    lines.append("git push origin main")
    lines.append("# origin = the name of the remote (GitHub)")
    lines.append("# main   = the branch name")
    lines.append("")
    lines.append("# GETTING latest changes from remote")
    lines.append("git pull             # fetch + merge in one step")
    lines.append("git fetch            # only download, do not merge yet")
    lines.append("git pull --rebase    # fetch + rebase instead of merge (cleaner)")
    lines.append("```")
    lines.append("")
    lines.append("**What makes a good commit message?**")
    lines.append("```")
    lines.append("Bad:  'changes'  'fix'  'wip'  'asdf'")
    lines.append("Good: 'feat: add password reset email flow'")
    lines.append("      'fix: null pointer in UserService.findById()'")
    lines.append("      'chore: upgrade spring-boot to 3.2.1'")
    lines.append("      'docs: add API endpoint documentation'")
    lines.append("")
    lines.append("Convention: <type>: <short summary>")
    lines.append("Types: feat, fix, chore, docs, refactor, test, style")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Branches — Working in Parallel")
    lines.append("")
    lines.append("A branch is just a **lightweight pointer** to a specific commit.")
    lines.append("Creating one is instant and costs almost nothing.")
    lines.append("")
    lines.append("```")
    lines.append("main branch:")
    lines.append("  A --- B --- C          <- production code, always working")
    lines.append("               \\")
    lines.append("feature/login:  D --- E  <- your new feature, in progress")
    lines.append("                         <- nobody else is affected until you merge")
    lines.append("```")
    lines.append("")
    lines.append("```bash")
    lines.append("git branch                    # list all branches (* = current)")
    lines.append("git branch feature/login      # create a new branch (does NOT switch to it)")
    lines.append("git checkout feature/login    # switch to a branch")
    lines.append("git checkout -b feature/login # create AND switch in one command (shortcut)")
    lines.append("git switch feature/login      # newer Git 2.23+ syntax for checkout")
    lines.append("git switch -c feature/login   # create + switch (newer syntax)")
    lines.append("")
    lines.append("# When feature is done: merge it back")
    lines.append("git checkout main")
    lines.append("git merge feature/login")
    lines.append("")
    lines.append("# Clean up the branch after merging")
    lines.append("git branch -d feature/login   # delete local branch")
    lines.append("git push origin --delete feature/login  # delete remote branch")
    lines.append("```")
    lines.append("")
    lines.append("**Real-world scenario:** Three developers on one team:")
    lines.append("```")
    lines.append("Alice  creates: feature/payment-gateway")
    lines.append("Bob    creates: feature/email-notifications")
    lines.append("Charlie creates: fix/login-timeout-bug")
    lines.append("")
    lines.append("All three branch FROM main.")
    lines.append("Each works independently — no interference.")
    lines.append("Each opens a Pull Request when done.")
    lines.append("Code review happens. Approved? Merge to main.")
    lines.append("Your CI/CD pipeline runs tests on every PR automatically.")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Merge vs Rebase — Explained Simply")
    lines.append("")
    lines.append("Both combine changes from one branch into another. The difference is HOW.")
    lines.append("")
    lines.append("**Merge** — joins two branches, creates a merge commit:")
    lines.append("```")
    lines.append("Before:")
    lines.append("  main:    A --- B --- C")
    lines.append("                \\")
    lines.append("  feature:  D --- E")
    lines.append("")
    lines.append("After: git checkout main && git merge feature")
    lines.append("  main:    A --- B --- C --- M   (M = merge commit)")
    lines.append("                \\           /")
    lines.append("  feature:  D --- E ---------")
    lines.append("")
    lines.append("History shows exactly WHEN branches met. Non-destructive.")
    lines.append("```")
    lines.append("")
    lines.append("**Rebase** — replays your commits on top of another branch:")
    lines.append("```")
    lines.append("Before:")
    lines.append("  main:    A --- B --- C")
    lines.append("                \\")
    lines.append("  feature:  D --- E")
    lines.append("")
    lines.append("After: git checkout feature && git rebase main")
    lines.append("  main:    A --- B --- C")
    lines.append("                       \\")
    lines.append("  feature:              D' --- E'  (rewritten commits)")
    lines.append("")
    lines.append("Linear history! D and E are rewritten with new hashes.")
    lines.append("```")
    lines.append("")
    lines.append("**When to use each:**")
    lines.append("```")
    lines.append("Merge:  merging feature branches into main (shows the full picture)")
    lines.append("Rebase: updating your feature branch with latest main changes (local only)")
    lines.append("")
    lines.append("GOLDEN RULE: Never rebase commits that others have already pulled.")
    lines.append("Rebase rewrites history. If Bob has your old commits, his branch")
    lines.append("will diverge and everything gets messy.")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Undoing Mistakes")
    lines.append("")
    lines.append("Git's safety net — every mistake is recoverable (mostly).")
    lines.append("")
    lines.append("```bash")
    lines.append("# UNDO UNSTAGED CHANGES (working tree)")
    lines.append("git restore filename.txt     # throw away changes to one file")
    lines.append("git restore .                # throw away ALL unstaged changes (careful!)")
    lines.append("")
    lines.append("# UNDO STAGED CHANGES (move back to working tree)")
    lines.append("git restore --staged filename.txt  # unstage a file")
    lines.append("")
    lines.append("# UNDO LAST COMMIT (but keep the changes)")
    lines.append("git reset --soft HEAD~1")
    lines.append("# HEAD~1 means 'one commit before current'")
    lines.append("# Changes go back to staging area — you can re-commit differently")
    lines.append("")
    lines.append("# UNDO LAST COMMIT AND DISCARD CHANGES (nuclear option)")
    lines.append("git reset --hard HEAD~1")
    lines.append("# WARNING: changes are gone from working tree too. No undo for this!")
    lines.append("")
    lines.append("# SAFE UNDO for shared branches: create an 'anti-commit'")
    lines.append("git revert abc1234")
    lines.append("# Creates a NEW commit that reverses the changes of abc1234")
    lines.append("# Safe because it does NOT rewrite history")
    lines.append("")
    lines.append("# FIX YOUR LAST COMMIT (before pushing)")
    lines.append("git commit --amend -m 'corrected message'")
    lines.append("# Or: add a forgotten file, then amend:")
    lines.append("git add forgotten-file.txt")
    lines.append("git commit --amend --no-edit")
    lines.append("```")
    lines.append("")
    lines.append("```")
    lines.append("Decision tree for undoing:")
    lines.append("")
    lines.append("Did I push yet?")
    lines.append("  NO:")
    lines.append("    Unstaged change  --> git restore filename")
    lines.append("    Staged change    --> git restore --staged filename")
    lines.append("    Wrong commit msg --> git commit --amend")
    lines.append("    Undo last commit --> git reset --soft HEAD~1")
    lines.append("  YES (already pushed to shared branch):")
    lines.append("    ALWAYS use git revert (never reset on shared branches!)")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Stashing — Saving Work in Progress")
    lines.append("")
    lines.append("You are in the middle of a feature and your boss says 'urgent bug fix needed now!'.")
    lines.append("You cannot commit half-done work. Stash saves it temporarily.")
    lines.append("")
    lines.append("```bash")
    lines.append("git stash             # save all uncommitted changes to a hidden stack")
    lines.append("                      # working tree becomes clean again")
    lines.append("")
    lines.append("git stash list        # see all saved stashes")
    lines.append("# stash@{0}: WIP on feature/login: abc123 half-done auth logic")
    lines.append("")
    lines.append("git stash pop         # restore the most recent stash and remove it")
    lines.append("git stash apply       # restore without removing (keeps it in list)")
    lines.append("")
    lines.append("git stash push -m 'half-done payment logic'  # stash with a label")
    lines.append("git stash drop stash@{0}                      # delete a specific stash")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Viewing History")
    lines.append("")
    lines.append("```bash")
    lines.append("git log                        # full commit history")
    lines.append("git log --oneline              # compact: one line per commit")
    lines.append("git log --oneline --graph --all # ASCII graph of all branches")
    lines.append("git log -5                     # last 5 commits only")
    lines.append("git log --author 'Alice'       # commits by Alice")
    lines.append("git log --since '2 weeks ago'  # commits from last 2 weeks")
    lines.append("git log -- filename.txt        # commits that touched filename.txt")
    lines.append("")
    lines.append("# See what changed in a specific commit")
    lines.append("git show abc1234")
    lines.append("")
    lines.append("# Who wrote each line of a file?")
    lines.append("git blame src/UserService.java")
    lines.append("# Output: each line prefixed with: hash (author date) line-number | code")
    lines.append("")
    lines.append("# Find which commit introduced a bug (binary search!)")
    lines.append("git bisect start")
    lines.append("git bisect bad         # current commit is broken")
    lines.append("git bisect good v1.0   # v1.0 was fine")
    lines.append("# Git checks out the mid-point commit, you test it")
    lines.append("git bisect good/bad    # tell Git the result, repeat")
    lines.append("# Git narrows down to the exact breaking commit")
    lines.append("git bisect reset       # exit bisect mode")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## .gitignore — What NOT to Track")
    lines.append("")
    lines.append("Some files should NEVER go into Git: build output, IDE configs, secrets.")
    lines.append("")
    lines.append("```")
    lines.append("# Create a .gitignore file in your project root:")
    lines.append("")
    lines.append("# Java build output")
    lines.append("target/")
    lines.append("*.class")
    lines.append("*.jar")
    lines.append("")
    lines.append("# Secrets — CRITICAL: never commit these!")
    lines.append(".env")
    lines.append("application-secrets.yml")
    lines.append("*.pem")
    lines.append("credentials.json")
    lines.append("")
    lines.append("# IDE files")
    lines.append(".idea/")
    lines.append("*.iml")
    lines.append(".vscode/")
    lines.append("")
    lines.append("# macOS")
    lines.append(".DS_Store")
    lines.append("")
    lines.append("# Node.js")
    lines.append("node_modules/")
    lines.append("```")
    lines.append("")
    lines.append("**CRITICAL MISTAKE — Committed a Secret:**")
    lines.append("```")
    lines.append("Scenario: You committed an AWS API key in application.properties")
    lines.append("Even if you delete it in the next commit, it is still in git history.")
    lines.append("Anyone who clones the repo can find it with: git log -p")
    lines.append("")
    lines.append("Solution:")
    lines.append("1. Immediately rotate/revoke the key (make the leaked key useless)")
    lines.append("2. Use BFG Repo Cleaner to remove it from history:")
    lines.append("   java -jar bfg.jar --delete-files application.properties")
    lines.append("3. Force-push the rewritten history")
    lines.append("4. Add the file to .gitignore")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## GitHub Flow — The Standard Team Workflow")
    lines.append("")
    lines.append("```")
    lines.append("1. Branch off main")
    lines.append("   git checkout -b feature/my-feature")
    lines.append("")
    lines.append("2. Commit your work")
    lines.append("   (many small commits with clear messages)")
    lines.append("")
    lines.append("3. Push to GitHub")
    lines.append("   git push origin feature/my-feature")
    lines.append("")
    lines.append("4. Open a Pull Request (PR) on GitHub")
    lines.append("   - Describe what you did and why")
    lines.append("   - Tag reviewers")
    lines.append("")
    lines.append("5. Code review")
    lines.append("   - Teammates comment on specific lines")
    lines.append("   - You push fixes as new commits")
    lines.append("")
    lines.append("6. CI/CD runs automated tests on your branch")
    lines.append("   - Must pass before merge")
    lines.append("")
    lines.append("7. Merge to main (squash-merge = one clean commit)")
    lines.append("")
    lines.append("8. Deploy (auto-triggered from main)")
    lines.append("")
    lines.append("9. Delete the feature branch")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Remote Repositories")
    lines.append("")
    lines.append("```bash")
    lines.append("git remote -v                         # see all remotes and their URLs")
    lines.append("git remote add origin https://github.com/user/repo.git  # add a remote")
    lines.append("git remote set-url origin <new-url>   # change remote URL")
    lines.append("")
    lines.append("git push -u origin main               # push and set upstream (first time)")
    lines.append("                                       # -u = --set-upstream")
    lines.append("git push                               # after -u is set, just this")
    lines.append("git push --force-with-lease            # force push safely (checks nobody else pushed)")
    lines.append("")
    lines.append("# Work with forks (common in open source)")
    lines.append("git remote add upstream https://github.com/original/repo.git")
    lines.append("git fetch upstream")
    lines.append("git merge upstream/main               # sync your fork with original")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Detached HEAD — What It Means")
    lines.append("")
    lines.append("```")
    lines.append("Normally, HEAD points to a branch name:")
    lines.append("  HEAD -> main -> commit abc123")
    lines.append("")
    lines.append("Detached HEAD: HEAD points directly to a commit hash:")
    lines.append("  HEAD -> commit abc123   (no branch!)")
    lines.append("")
    lines.append("How you get here:")
    lines.append("  git checkout abc1234   (checking out a specific old commit)")
    lines.append("  git checkout v1.2.3    (checking out a tag)")
    lines.append("")
    lines.append("What it means:")
    lines.append("  You can look around and experiment.")
    lines.append("  Any new commits you make are NOT connected to any branch.")
    lines.append("  If you switch away, those commits become unreachable (lost!).")
    lines.append("")
    lines.append("How to save work done in detached HEAD:")
    lines.append("  git checkout -b my-experiment   <- creates a branch HERE")
    lines.append("  Now your commits are safe on 'my-experiment' branch.")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Mind Map — Everything at a Glance")
    lines.append("")
    lines.append("```")
    lines.append("GIT FUNDAMENTALS")
    lines.append("|")
    lines.append("+-- THREE AREAS")
    lines.append("|   +-- Working Tree (your files)")
    lines.append("|   +-- Staging Area (git add)")
    lines.append("|   +-- Repository   (git commit)")
    lines.append("|")
    lines.append("+-- CORE WORKFLOW")
    lines.append("|   +-- git status    (what changed?)")
    lines.append("|   +-- git add       (stage changes)")
    lines.append("|   +-- git commit    (save snapshot)")
    lines.append("|   +-- git push      (upload to remote)")
    lines.append("|   +-- git pull      (download + merge)")
    lines.append("|")
    lines.append("+-- BRANCHES")
    lines.append("|   +-- git checkout -b (create + switch)")
    lines.append("|   +-- git merge       (join branches)")
    lines.append("|   +-- git rebase      (linearize history)")
    lines.append("|   +-- Pull Requests   (code review flow)")
    lines.append("|")
    lines.append("+-- UNDOING")
    lines.append("|   +-- git restore      (discard changes)")
    lines.append("|   +-- git reset --soft (undo commit, keep changes)")
    lines.append("|   +-- git reset --hard (undo + discard)")
    lines.append("|   +-- git revert       (safe undo for shared branches)")
    lines.append("|   +-- git commit --amend (fix last commit)")
    lines.append("|")
    lines.append("+-- UTILITIES")
    lines.append("|   +-- git stash         (save WIP temporarily)")
    lines.append("|   +-- git log --graph   (visual history)")
    lines.append("|   +-- git blame         (who wrote this line?)")
    lines.append("|   +-- git bisect        (find breaking commit)")
    lines.append("|   +-- .gitignore        (exclude files)")
    lines.append("|")
    lines.append("+-- REMOTES")
    lines.append("    +-- origin            (your GitHub fork/repo)")
    lines.append("    +-- upstream          (original repo)")
    lines.append("    +-- git push/pull/fetch")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## How Git Connects to Other Topics")
    lines.append("")
    lines.append("- **CI/CD Pipelines**: Every git push triggers your pipeline. Branch strategy")
    lines.append("  defines deployment flow. Merging to main = auto-deploy to production.")
    lines.append("- **Docker**: Images are often tagged with git commit hashes (`image:abc1234`).")
    lines.append("  Dockerfiles live in the git repo.")
    lines.append("- **Linux**: You run all git commands from the bash terminal.")
    lines.append("  Bash scripting skills help automate git workflows.")
    lines.append("- **Code Review / PRs**: GitHub, GitLab, Bitbucket are all built on top of Git.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Common Beginner Mistakes")
    lines.append("")
    lines.append("1. **Committing directly to main** — always branch. main should only receive merges.")
    lines.append("2. **Vague commit messages** — 'fix stuff' is useless. Future-you will hate present-you.")
    lines.append("3. **git add .** always — review what you stage. Use `git status` first.")
    lines.append("4. **Committing .env or secrets** — add to .gitignore BEFORE first commit.")
    lines.append("5. **git reset --hard on shared branches** — destroys history others have pulled.")
    lines.append("   Use `git revert` instead.")
    lines.append("6. **Not pulling before pushing** — leads to rejected pushes. Always `git pull` first.")
    lines.append("7. **Rebase on shared branches** — rewrites history others depend on. Chaos ensues.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## References and Further Learning")
    lines.append("")
    lines.append("### Videos (Watch These!)")
    lines.append("- **Git and GitHub for Beginners - Crash Course** by freeCodeCamp:")
    lines.append("  https://www.youtube.com/watch?v=RGOj5yH7evk")
    lines.append("  - 1 hour. Covers everything from init to pull requests. Best starting point.")
    lines.append("- **13 Advanced Git Tips and Tricks** by Fireship:")
    lines.append("  https://www.youtube.com/watch?v=ecK3EnyGD8o")
    lines.append("  - 8 minutes. Fast-paced demos of stash, bisect, reflog, and more.")
    lines.append("")
    lines.append("### Free Books and Articles")
    lines.append("- **Pro Git Book** (official, free, complete): https://git-scm.com/book")
    lines.append("  - The definitive Git reference. Chapters 1-3 are essential for beginners.")
    lines.append("- **Oh Shit, Git!** (common mistakes and how to fix them): https://ohshitgit.com/")
    lines.append("  - Bookmark this. When you mess up (you will), this has the exact fix.")
    lines.append("")
    lines.append("### Diagrams and Cheatsheets")
    lines.append("- **Git Visual Cheatsheet**: https://ndpsoftware.com/git-cheatsheet.html")
    lines.append("  - Interactive diagram showing how commands move changes between the three areas.")
    lines.append("- **GitHub Git Cheatsheet** (PDF): https://education.github.com/git-cheat-sheet-education.pdf")
    lines.append("")
    lines.append("### Practice")
    lines.append("- **Learn Git Branching** (visual interactive): https://learngitbranching.js.org/")
    lines.append("  - Best interactive Git tutorial. Visualizes branches as you type commands.")
    lines.append("- **GitHub Skills**: https://skills.github.com/")
    lines.append("  - Hands-on courses directly in GitHub repos.")

    NEW_GUIDE = "\n".join(lines)

    d['guide'] = NEW_GUIDE
    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"Done! Guide length: {len(NEW_GUIDE)} chars")
    print(f"Questions: {len(d['questions'])}, Flashcards: {len(d['flashcards'])}")
    print(f"Has YouTube links: {'youtube.com' in NEW_GUIDE}")
    print(f"Has References section: {'References' in NEW_GUIDE}")

    # ── patch_docker.py ──────────────────────────────────────────────────────────────────
    p = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/docker.json')
    d = json.loads(p.read_text())

    # ── GUIDE ─────────────────────────────────────────────────────────────────────
    lines = []
    lines += [
        "# Docker",
        "",
        "## What Is Docker? (Zero Assumptions)",
        "",
        "Picture this: you build a Java Spring Boot app on your MacBook. It works perfectly.",
        "You deploy it to an Ubuntu server — it crashes. 'Works on my machine!' is the classic",
        "developer nightmare. Different OS, different Java version, different library versions,",
        "missing environment variables — anything can go wrong.",
        "",
        "Docker solves this by packaging your **app + everything it needs** into one unit called",
        "a **container**. The container runs identically everywhere — your laptop, a colleague's",
        "Windows machine, an AWS server, a CI/CD pipeline. Same result, every time.",
        "",
        "**Analogy:** Think of a Docker container like a shipping container on a cargo ship.",
        "Before shipping containers existed, cargo was loaded piece by piece — slow, inconsistent,",
        "error-prone. Shipping containers standardised everything: same box, same crane interface,",
        "works on any ship or truck. Docker does the same for software.",
        "",
        "```",
        "Without Docker:                    With Docker:",
        "  Your laptop: Java 17              Container image packages:",
        "  Server:      Java 11              - Your app .jar",
        "  CI server:   Java 21              - Java 17 (exact version)",
        "  'It works on my machine!'         - All dependencies",
        "                                    - Config files",
        "                                    Runs IDENTICALLY everywhere",
        "```",
        "",
        "---",
        "",
        "## Virtual Machines vs Containers",
        "",
        "Both give you an isolated environment, but they work very differently:",
        "",
        "```",
        "VIRTUAL MACHINE:                    CONTAINER:",
        "",
        "+---------------------------+        +---------------------------+",
        "| App A      | App B        |        | App A  | App B  | App C  |",
        "| (Node.js)  | (Java)       |        +--------+--------+--------+",
        "+------------+--------------+        | Container Runtime (runc) |",
        "| Guest OS A | Guest OS B   |        +---------------------------+",
        "| (Ubuntu)   | (Windows)    |        | Host OS Kernel (Linux)   |",
        "+------------+--------------+        +---------------------------+",
        "| Hypervisor (VMware/VBox)  |        | Physical Hardware         |",
        "+---------------------------+        +---------------------------+",
        "| Physical Hardware         |",
        "+---------------------------+",
        "",
        "VM:        Each app has its OWN full OS = heavy (GBs), slow to start (minutes)",
        "Container: Apps SHARE the host OS kernel = light (MBs), starts in seconds",
        "```",
        "",
        "**Key differences:**",
        "| Feature | Virtual Machine | Container |",
        "| --- | --- | --- |",
        "| Startup time | 1-5 minutes | Under 1 second |",
        "| Size | 1-20 GB | 10-500 MB |",
        "| Isolation | Full OS isolation | Process isolation |",
        "| OS | Each VM has its own | Shares host kernel |",
        "| Use case | Full environment isolation | App packaging and deployment |",
        "",
        "---",
        "",
        "## Core Concepts: Image vs Container",
        "",
        "This is the most important distinction to understand:",
        "",
        "```",
        "IMAGE                               CONTAINER",
        "(a blueprint / recipe)              (a running instance)",
        "",
        "Like a class in OOP                 Like an object (instance of the class)",
        "Like a cookie cutter                Like an actual cookie",
        "Like a CD-ROM with the OS           Like a running OS on your machine",
        "",
        "Read-only snapshot                  Running process with its own memory,",
        "stored on disk                      filesystem, network",
        "",
        "You BUILD images                    You RUN containers FROM images",
        "You PUSH images to registries       You can run many containers",
        "You PULL images to machines         from the same image",
        "```",
        "",
        "**Docker Hub** is the public registry where images live:",
        "- `nginx` = official Nginx web server image",
        "- `postgres:15` = PostgreSQL version 15",
        "- `openjdk:17-slim` = lean Java 17 runtime",
        "- `yourusername/myapp:v1.2` = your own custom image",
        "",
        "---",
        "",
        "## Installing Docker and First Commands",
        "",
        "```bash",
        "# Install on Ubuntu",
        "sudo apt update",
        "sudo apt install docker.io",
        "sudo systemctl start docker",
        "sudo systemctl enable docker  # start on boot",
        "",
        "# Add yourself to docker group (avoid needing sudo every time)",
        "sudo usermod -aG docker $USER",
        "# Log out and back in for this to take effect",
        "",
        "# Verify installation",
        "docker --version",
        "docker run hello-world   # downloads and runs a test container",
        "```",
        "",
        "---",
        "",
        "## Essential Docker Commands",
        "",
        "```bash",
        "# IMAGES",
        "docker images                    # list images on your machine",
        "docker pull nginx                # download nginx image from Docker Hub",
        "docker pull postgres:15          # specific version tag",
        "docker rmi nginx                 # remove an image",
        "docker image prune               # remove all unused images",
        "",
        "# RUNNING CONTAINERS",
        "docker run nginx                 # start a container (foreground, blocks terminal)",
        "docker run -d nginx              # -d = detached (background), returns container ID",
        "docker run -d -p 8080:80 nginx   # -p host_port:container_port (port mapping)",
        "                                  # now http://localhost:8080 hits nginx inside container",
        "docker run -d --name my-nginx nginx  # give container a name (easier to reference)",
        "docker run --rm nginx            # --rm = auto-delete when container stops",
        "",
        "# VIEWING CONTAINERS",
        "docker ps                        # list RUNNING containers",
        "docker ps -a                     # list ALL containers (including stopped)",
        "docker logs my-nginx             # see container output/logs",
        "docker logs -f my-nginx          # follow logs live (like tail -f)",
        "docker stats                     # live CPU/memory usage of all containers",
        "",
        "# MANAGING CONTAINERS",
        "docker stop my-nginx             # graceful stop (SIGTERM, waits for cleanup)",
        "docker kill my-nginx             # force stop (SIGKILL immediately)",
        "docker start my-nginx            # restart a stopped container",
        "docker rm my-nginx               # delete a stopped container",
        "docker rm -f my-nginx            # force remove running container",
        "",
        "# GOING INSIDE A CONTAINER (like SSH)",
        "docker exec -it my-nginx bash    # open interactive bash terminal inside container",
        "docker exec -it my-nginx sh      # use sh if bash not available (Alpine images)",
        "# -i = interactive  -t = allocate a pseudo-TTY (needed for terminal)",
        "",
        "# COPYING FILES",
        "docker cp my-nginx:/etc/nginx/nginx.conf ./   # copy FROM container to host",
        "docker cp ./app.jar my-container:/app/        # copy FROM host TO container",
        "```",
        "",
        "**Port mapping explained:**",
        "```",
        "docker run -d -p 8080:80 nginx",
        "                  |   |",
        "                  |   +-- container port (nginx listens on 80 inside)",
        "                  +------- host port (you access via localhost:8080)",
        "",
        "Browser: http://localhost:8080",
        "                    |",
        "                    | Docker NAT",
        "                    v",
        "        Container port 80 (nginx)",
        "```",
        "",
        "---",
        "",
        "## The Dockerfile — Building Your Own Image",
        "",
        "A `Dockerfile` is a recipe that tells Docker how to build your image.",
        "Each instruction creates a new **layer** (cached).",
        "",
        "```dockerfile",
        "# Start FROM an existing base image",
        "FROM openjdk:17-slim",
        "",
        "# Set the working directory inside the container",
        "WORKDIR /app",
        "",
        "# COPY files from host into the image",
        "# Copy pom.xml FIRST (changes rarely) — layer cache trick",
        "COPY pom.xml .",
        "COPY src ./src",
        "",
        "# RUN a command during image BUILD (not at runtime)",
        "RUN ./mvnw package -DskipTests",
        "",
        "# Declare which port the app listens on (documentation only, does not publish)",
        "EXPOSE 8080",
        "",
        "# Set an environment variable",
        "ENV SPRING_PROFILES_ACTIVE=production",
        "",
        "# CMD = default command when container STARTS (can be overridden)",
        "CMD [\"java\", \"-jar\", \"target/app.jar\"]",
        "",
        "# ENTRYPOINT = fixed command, CMD becomes its arguments",
        "# ENTRYPOINT [\"java\", \"-jar\", \"target/app.jar\"]",
        "```",
        "",
        "**Build and run your image:**",
        "```bash",
        "docker build -t myapp:v1 .          # build image, tag as myapp:v1, use current dir",
        "docker build -t myapp:v1 -f Dockerfile.prod .  # use specific Dockerfile",
        "docker run -d -p 8080:8080 myapp:v1",
        "```",
        "",
        "---",
        "",
        "## Layer Caching — Why Order Matters",
        "",
        "Docker caches each layer. If a layer has not changed, it reuses the cache.",
        "This makes rebuilds much faster. Order your Dockerfile to maximise cache hits.",
        "",
        "```",
        "BAD ORDER (slow rebuilds):",
        "  COPY . .              <- copies ALL source code (changes every edit)",
        "  RUN mvn install       <- runs every time because source changed",
        "",
        "GOOD ORDER (fast rebuilds):",
        "  COPY pom.xml .        <- pom.xml changes rarely -> layer cache usually HIT",
        "  RUN mvn dependency:go-offline  <- downloads deps once, cached",
        "  COPY src ./src        <- source changes often, but only this layer reruns",
        "  RUN mvn package       <- only reruns if src changed",
        "",
        "Layer cache logic:",
        "  If layer N changes -> ALL layers after N must rebuild",
        "  Put rarely-changing steps FIRST, frequently-changing steps LAST",
        "```",
        "",
        "---",
        "",
        "## Multi-Stage Builds — Smaller Production Images",
        "",
        "Problem: your build tools (Maven, npm) are only needed during build — not at runtime.",
        "Multi-stage builds let you build in one container and copy only the output to a lean image.",
        "",
        "```dockerfile",
        "# STAGE 1: build (has Maven, JDK, all build tools — big image)",
        "FROM maven:3.9-openjdk-17 AS builder",
        "WORKDIR /build",
        "COPY pom.xml .",
        "RUN mvn dependency:go-offline",
        "COPY src ./src",
        "RUN mvn package -DskipTests",
        "",
        "# STAGE 2: runtime (only JRE, no Maven, no source code — tiny image)",
        "FROM openjdk:17-slim AS runtime",
        "WORKDIR /app",
        "COPY --from=builder /build/target/app.jar app.jar",
        "EXPOSE 8080",
        "CMD [\"java\", \"-jar\", \"app.jar\"]",
        "",
        "# Result: builder image = ~800MB, runtime image = ~180MB",
        "# Only the runtime stage is shipped to production",
        "```",
        "",
        "---",
        "",
        "## Docker Volumes — Persistent Data",
        "",
        "Containers are ephemeral — when you remove a container, all data inside is lost.",
        "Volumes let you persist data outside the container lifecycle.",
        "",
        "```bash",
        "# Named volume (Docker manages storage location)",
        "docker volume create mydata",
        "docker run -d -v mydata:/var/lib/postgresql/data postgres:15",
        "# Database data survives container removal",
        "",
        "# Bind mount (maps a host directory into the container)",
        "docker run -d -v /home/alice/config:/app/config myapp",
        "# /home/alice/config on host IS /app/config inside container",
        "# Changes on either side are immediately visible to the other",
        "",
        "# List volumes",
        "docker volume ls",
        "docker volume inspect mydata",
        "docker volume rm mydata       # delete (data gone!)",
        "```",
        "",
        "```",
        "Volume types:",
        "  Named volume:    Docker stores at /var/lib/docker/volumes/mydata/",
        "                   Good for databases, persistent state",
        "  Bind mount:      You choose the host directory",
        "                   Good for config files, development (live code reload)",
        "  tmpfs mount:     In-memory only, never written to disk",
        "                   Good for sensitive temp data",
        "```",
        "",
        "---",
        "",
        "## Docker Compose — Multi-Container Apps",
        "",
        "Real apps have multiple services: web server, database, cache, queue.",
        "Docker Compose lets you define and run them all with one file.",
        "",
        "```yaml",
        "# docker-compose.yml",
        "version: '3.8'",
        "",
        "services:",
        "  app:                          # your Spring Boot app",
        "    build: .                    # build from Dockerfile in current dir",
        "    ports:",
        "      - '8080:8080'",
        "    environment:",
        "      - SPRING_DATASOURCE_URL=jdbc:postgresql://db:5432/mydb",
        "      - SPRING_DATASOURCE_PASSWORD=secret",
        "    depends_on:",
        "      - db                      # wait for db service to start",
        "    networks:",
        "      - backend",
        "",
        "  db:                           # PostgreSQL database",
        "    image: postgres:15",
        "    environment:",
        "      - POSTGRES_DB=mydb",
        "      - POSTGRES_PASSWORD=secret",
        "    volumes:",
        "      - pgdata:/var/lib/postgresql/data",
        "    networks:",
        "      - backend",
        "",
        "  redis:                        # Redis cache",
        "    image: redis:7-alpine",
        "    networks:",
        "      - backend",
        "",
        "volumes:",
        "  pgdata:                       # named volume for database",
        "",
        "networks:",
        "  backend:                      # private network — services talk to each other by service name",
        "```",
        "",
        "```bash",
        "docker compose up -d       # start all services in background",
        "docker compose down        # stop and remove containers",
        "docker compose down -v     # also delete volumes (wipes database!)",
        "docker compose logs -f app # follow logs for 'app' service",
        "docker compose ps          # status of all services",
        "docker compose exec app bash  # shell into running 'app' container",
        "docker compose build       # rebuild images",
        "```",
        "",
        "**How services find each other:** Inside a Compose network, services reach each other",
        "by their service name. Your app connects to `db:5432` — Docker DNS resolves `db`",
        "to the database container's IP automatically.",
        "",
        "---",
        "",
        "## Docker Networking",
        "",
        "```",
        "Default networks:",
        "  bridge:  Default for standalone containers. Containers can communicate",
        "           via IP but not by name (use user-defined networks instead)",
        "  host:    Container shares host network stack (no isolation)",
        "           Use only when performance is critical",
        "  none:    No networking at all",
        "",
        "User-defined bridge network (best practice):",
        "  docker network create mynet",
        "  docker run -d --network mynet --name app myapp",
        "  docker run -d --network mynet --name db postgres:15",
        "  Now 'app' can reach 'db' by hostname 'db' — automatic DNS resolution",
        "```",
        "",
        "---",
        "",
        "## Environment Variables and Secrets",
        "",
        "```bash",
        "# Pass env vars at runtime",
        "docker run -e DB_PASSWORD=secret myapp",
        "docker run --env-file .env myapp    # load from file",
        "",
        "# In docker-compose.yml",
        "# environment:",
        "#   - DB_PASSWORD=${DB_PASSWORD}    # reads from host environment",
        "",
        "# .env file (NEVER commit to git!)",
        "# DB_PASSWORD=supersecret",
        "# API_KEY=abc123",
        "```",
        "",
        "**Rule:** Never hardcode secrets in Dockerfiles or docker-compose.yml.",
        "Use environment variables loaded from a `.env` file (in `.gitignore`)",
        "or a secrets manager (AWS Secrets Manager, Vault).",
        "",
        "---",
        "",
        "## Mind Map",
        "",
        "```",
        "DOCKER",
        "|",
        "+-- CONCEPTS",
        "|   +-- Image  = blueprint (read-only)",
        "|   +-- Container = running instance",
        "|   +-- Registry = image storage (Docker Hub)",
        "|   +-- Layer = cached filesystem change",
        "|",
        "+-- DOCKERFILE",
        "|   +-- FROM (base image)",
        "|   +-- COPY (add files)",
        "|   +-- RUN  (build-time commands)",
        "|   +-- CMD  (runtime default command)",
        "|   +-- EXPOSE (document port)",
        "|   +-- Multi-stage (small prod images)",
        "|",
        "+-- COMMANDS",
        "|   +-- docker build -t name .",
        "|   +-- docker run -d -p host:container",
        "|   +-- docker exec -it name bash",
        "|   +-- docker logs -f name",
        "|   +-- docker ps / docker ps -a",
        "|",
        "+-- DATA",
        "|   +-- Volume (persistent, managed)",
        "|   +-- Bind mount (host directory)",
        "|",
        "+-- COMPOSE",
        "|   +-- docker-compose.yml",
        "|   +-- services, networks, volumes",
        "|   +-- docker compose up/down",
        "|",
        "+-- NETWORKING",
        "    +-- bridge (default)",
        "    +-- user-defined (DNS by name)",
        "    +-- host (no isolation)",
        "```",
        "",
        "---",
        "",
        "## How Docker Connects to Other Topics",
        "",
        "- **Kubernetes**: K8s orchestrates Docker containers at scale.",
        "  Every K8s pod runs container images built with Docker.",
        "- **CI/CD**: Pipelines build Docker images on every commit and push to a registry.",
        "- **Linux**: Containers ARE Linux processes. `docker exec -it` drops you into a",
        "  Linux shell. All Linux skills (permissions, processes, logs) apply inside containers.",
        "- **Microservices**: Docker enables each service to have its own isolated environment,",
        "  dependencies, and runtime — making microservice architectures practical.",
        "",
        "---",
        "",
        "## Common Beginner Mistakes",
        "",
        "1. **Running as root inside container** — use `USER appuser` in Dockerfile for security.",
        "2. **Storing secrets in Dockerfile or image** — they become visible in `docker history`.",
        "3. **Using `latest` tag in production** — `nginx:latest` changes over time, breaking reproducibility. Always pin versions: `nginx:1.25.3`.",
        "4. **Huge images** — use slim/alpine base images, multi-stage builds, add `.dockerignore`.",
        "5. **No `.dockerignore`** — COPY . . copies node_modules, .git, logs. Add `.dockerignore` like `.gitignore`.",
        "6. **Data loss** — removing a container without volumes deletes all its data.",
        "7. **Port conflicts** — two containers cannot bind the same host port. Use different host ports.",
        "",
        "---",
        "",
        "## References and Further Learning",
        "",
        "### Videos (Watch These!)",
        "- **Docker Tutorial for Beginners** by TechWorld with Nana:",
        "  https://www.youtube.com/watch?v=3c-iBn73dDE",
        "  - 3 hours. Covers containers, images, Dockerfile, Compose, volumes. Best beginner course.",
        "- **Docker in 100 Seconds** by Fireship:",
        "  https://www.youtube.com/watch?v=Gjnup-PuquQ",
        "  - 2 minutes. Perfect high-level mental model before going deep.",
        "",
        "### Free Books and Articles",
        "- **Docker official docs - Get Started guide**: https://docs.docker.com/get-started/",
        "  - Official beginner tutorial. Do Parts 1-5.",
        "- **Play with Docker** (free browser-based Docker lab): https://labs.play-with-docker.com/",
        "  - No installation needed. Spin up Linux VMs with Docker in browser.",
        "",
        "### Diagrams and Cheatsheets",
        "- **Docker Cheatsheet by wsargent**: https://github.com/wsargent/docker-cheat-sheet",
        "  - Comprehensive command reference with explanations.",
        "- **Container vs VM diagram**: search 'Docker vs VM architecture diagram' on Google Images.",
        "",
        "### Practice",
        "- **KodeKloud Docker for Beginners** (free course with browser labs):",
        "  https://kodekloud.com/courses/docker-for-the-absolute-beginner/",
        "- **DockerLabs**: https://dockerlabs.collabnix.com/",
        "  - 100+ hands-on labs from beginner to advanced.",
    ]

    DOCKER_GUIDE = "\n".join(lines)

    # ── QUESTIONS ─────────────────────────────────────────────────────────────────
    NEW_QUESTIONS = [
        {"id":"dkr-q4","type":"mcq",
         "prompt":"What is the difference between a Docker image and a container?",
         "choices":["They are the same thing","An image is a read-only blueprint; a container is a running instance of that image","A container is read-only; an image is running","Images run on VMs; containers run on bare metal"],
         "answerIndex":1,"explanation":"Image = static blueprint stored on disk (like a class). Container = live running instance of that image (like an object). You can run many containers from one image.","tags":["docker-basics","image"]},
        {"id":"dkr-q5","type":"mcq",
         "prompt":"What does `docker run -d -p 8080:80 nginx` do?",
         "choices":["Runs nginx in foreground on port 80","Runs nginx detached in background, maps host port 8080 to container port 80","Runs nginx on port 8080 inside the container","Downloads nginx without running it"],
         "answerIndex":1,"explanation":"-d = detached (background). -p 8080:80 maps host port 8080 to container port 80. Accessing localhost:8080 on the host reaches nginx inside the container.","tags":["docker-run","ports"]},
        {"id":"dkr-q6","type":"mcq",
         "prompt":"Which Dockerfile instruction runs a command AT BUILD TIME (not at container start)?",
         "choices":["CMD","ENTRYPOINT","RUN","EXEC"],
         "answerIndex":2,"explanation":"RUN executes during image build (e.g. apt install, mvn package). CMD and ENTRYPOINT define what runs when the container starts. EXEC is not a Dockerfile instruction.","tags":["dockerfile","layers"]},
        {"id":"dkr-q7","type":"mcq",
         "prompt":"You want your Spring Boot container to persist database files after the container is removed. What should you use?",
         "choices":["COPY instruction","docker exec","Docker volume","Multi-stage build"],
         "answerIndex":2,"explanation":"Volumes persist data outside the container lifecycle. When the container is removed, the volume data survives. COPY, exec, and multi-stage are unrelated to data persistence.","tags":["volumes","persistence"]},
        {"id":"dkr-q8","type":"mcq",
         "prompt":"What does `docker exec -it myapp bash` do?",
         "choices":["Builds the myapp image","Starts a new container from myapp","Opens an interactive bash shell INSIDE the running myapp container","Stops the myapp container"],
         "answerIndex":2,"explanation":"exec runs a command inside an ALREADY RUNNING container. -it = interactive terminal. This is how you 'SSH into' a container to debug it.","tags":["docker-exec","debugging"]},
        {"id":"dkr-q9","type":"mcq",
         "prompt":"What is the primary benefit of Docker multi-stage builds?",
         "choices":["Faster runtime performance","Smaller production images by excluding build tools and source code","Automatic scaling","Better networking"],
         "answerIndex":1,"explanation":"Multi-stage builds let you compile in a large image (with Maven/npm etc.) and copy only the output artifact to a lean runtime image. Result: images shrink from ~800MB to ~180MB.","tags":["dockerfile","multi-stage"]},
        {"id":"dkr-q10","type":"mcq",
         "prompt":"Why should you add a `.dockerignore` file to your project?",
         "choices":["It speeds up container networking","It prevents COPY . . from including node_modules, .git, logs in the image — keeping images small and secure","It's required for docker-compose","It sets environment variables"],
         "answerIndex":1,"explanation":".dockerignore works like .gitignore — it excludes files from the build context sent to Docker daemon. Without it, COPY . . includes node_modules (hundreds of MB), .git history, and local config files.","tags":["dockerfile","best-practices"]},
        {"id":"dkr-q11","type":"mcq",
         "prompt":"In docker-compose, services in the same user-defined network reach each other by:",
         "choices":["IP addresses only","Their service names (Docker DNS resolves them automatically)","Port numbers","Container IDs"],
         "answerIndex":1,"explanation":"Docker Compose creates a network where services discover each other by service name. app can connect to db:5432 and Docker DNS resolves 'db' to the database container's IP.","tags":["compose","networking"]},
        {"id":"dkr-q12","type":"mcq",
         "prompt":"What happens to data inside a container when you run `docker rm mycontainer`?",
         "choices":["Data is automatically backed up","Data persists in the image","Data is permanently lost unless stored in a volume or bind mount","Data moves to /tmp on the host"],
         "answerIndex":2,"explanation":"Containers are ephemeral. Their writable layer is deleted with the container. Only data in volumes or bind mounts persists. This is why databases must use volumes.","tags":["volumes","containers"]},
        {"id":"dkr-q13","type":"mcq",
         "prompt":"Which base image choice results in the smallest production image?",
         "choices":["ubuntu:22.04","openjdk:17","openjdk:17-slim or eclipse-temurin:17-alpine","debian:latest"],
         "answerIndex":2,"explanation":"slim and alpine variants strip out non-essential packages. Alpine Linux is ~5MB vs ubuntu at ~70MB. openjdk:17-slim is ~250MB vs openjdk:17 at ~470MB.","tags":["dockerfile","image-size"]},
        {"id":"dkr-q14","type":"codeOutput",
         "prompt":"What does this command output?",
         "code":"docker ps -a | grep Exited | wc -l",
         "choices":["Number of running containers","Number of all containers","Number of stopped (Exited) containers","Error — invalid syntax"],
         "answerIndex":2,"explanation":"docker ps -a lists all containers including stopped. grep Exited filters only stopped ones. wc -l counts matching lines. Result = count of stopped containers.","tags":["docker-commands","pipes"]},
        {"id":"dkr-q15","type":"mcq",
         "prompt":"You hardcode `ENV DB_PASSWORD=mypassword` in your Dockerfile. What is the security risk?",
         "choices":["No risk — env vars are encrypted in images","The password is visible via `docker history` and to anyone who has the image","It causes a build error","The container cannot start"],
         "answerIndex":1,"explanation":"docker history shows every layer including ENV instructions in plain text. Anyone with access to the image can read the password. Always pass secrets via -e flag or --env-file at runtime.","tags":["security","dockerfile"]},
        {"id":"dkr-q16","type":"mcq",
         "prompt":"What is the correct Dockerfile instruction order for maximum layer cache efficiency in a Java project?",
         "choices":["COPY src -> RUN mvn install -> COPY pom.xml","COPY pom.xml -> RUN mvn dependency:go-offline -> COPY src -> RUN mvn package","COPY . . -> RUN mvn package","RUN mvn package -> COPY . ."],
         "answerIndex":1,"explanation":"pom.xml changes rarely, so its layer is cached. Dependencies download once. Source code changes frequently, so it goes last. If only src changes, only the last two layers rebuild — much faster.","tags":["dockerfile","layer-cache"]},
        {"id":"dkr-q17","type":"multi",
         "prompt":"Which of these should you include in a `.dockerignore` file? (Select all that apply)",
         "choices":["node_modules/",".git/",".env","src/main/java/"],
         "answerIndexes":[0,1,2],"explanation":"node_modules (huge), .git (exposes history), .env (contains secrets) should all be ignored. Source code (src/) must be included for the build to work.","tags":["dockerfile","security"]},
        {"id":"dkr-q18","type":"mcq",
         "prompt":"What does `docker compose down -v` do differently than `docker compose down`?",
         "choices":["They are identical","down -v also removes named volumes defined in compose file — deletes persistent data","down -v removes all images","down -v is faster"],
         "answerIndex":1,"explanation":"docker compose down stops and removes containers and networks. -v additionally removes named volumes. This deletes database data, uploaded files etc. Use with caution in production.","tags":["compose","volumes"]},
        {"id":"dkr-q19","type":"mcq",
         "prompt":"In a Dockerfile, what is the difference between CMD and ENTRYPOINT?",
         "choices":["CMD runs at build time; ENTRYPOINT at runtime","ENTRYPOINT = fixed command (hard to override); CMD = default arguments (easy to override)","They are identical","ENTRYPOINT is for Linux only"],
         "answerIndex":1,"explanation":"ENTRYPOINT sets the main executable — it runs every time. CMD provides default arguments to ENTRYPOINT, easily overridden. Together: ENTRYPOINT=[java -jar] CMD=[app.jar] allows: docker run myapp different.jar","tags":["dockerfile","cmd-entrypoint"]},
        {"id":"dkr-q20","type":"mcq",
         "prompt":"Why should you avoid using `image:latest` tag in production deployments?",
         "choices":["latest is too large","latest is not cached","latest points to whatever the newest version is — it changes over time, making deployments non-reproducible and breaking things unexpectedly","latest requires internet access"],
         "answerIndex":2,"explanation":"latest is a moving target. nginx:latest today might be 1.25, tomorrow 1.26 with breaking changes. Always pin: nginx:1.25.3. Your production config should be immutable and reproducible.","tags":["best-practices","tags"]},
    ]

    # ── FLASHCARDS ─────────────────────────────────────────────────────────────────
    NEW_FLASHCARDS = [
        {"id":"dkr-fc5","front":"docker run flags: -d -p -v -e --name","back":"-d=detached(background)  -p host:container port mapping  -v volume/bind mount  -e environment variable  --name give container a name","tags":["docker-run"]},
        {"id":"dkr-fc6","front":"Layer cache order rule","back":"Put rarely-changing steps first (COPY pom.xml, RUN mvn dependency:go-offline), frequently-changing steps last (COPY src, RUN mvn package). Any changed layer invalidates all subsequent layers.","tags":["dockerfile","performance"]},
        {"id":"dkr-fc7","front":"Container data persistence rule","back":"Containers are ephemeral — data inside is gone on rm. Use named volumes for databases/state. Use bind mounts in development for live code. Never rely on container filesystem for important data.","tags":["volumes","data"]},
        {"id":"dkr-fc8","front":"Secrets in Docker — the rule","back":"Never put secrets in Dockerfile ENV or image layers. Pass at runtime: docker run -e KEY=val or --env-file .env. Use Docker Secrets or AWS Secrets Manager in production. docker history reveals all image layers.","tags":["security","secrets"]},
    ]

    # ── WRITE ──────────────────────────────────────────────────────────────────────
    d['guide'] = DOCKER_GUIDE

    existing_q_ids = {q['id'] for q in d['questions']}
    for q in NEW_QUESTIONS:
        if q['id'] not in existing_q_ids:
            d['questions'].append(q)

    existing_fc_ids = {fc['id'] for fc in d['flashcards']}
    for fc in NEW_FLASHCARDS:
        if fc['id'] not in existing_fc_ids:
            d['flashcards'].append(fc)

    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

    print(f"docker.json done!")
    print(f"  Guide: {len(DOCKER_GUIDE)} chars")
    print(f"  Questions: {len(d['questions'])}")
    print(f"  Flashcards: {len(d['flashcards'])}")
    print(f"  YouTube: {'youtube.com' in DOCKER_GUIDE}")
    print(f"  References: {'References' in DOCKER_GUIDE}")

    # ── patch_k8s.py ──────────────────────────────────────────────────────────────────
    p = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/kubernetes.json')
    d = json.loads(p.read_text())

    lines = []
    lines += [
        "# Kubernetes",
        "",
        "## What Is Kubernetes? (No Prior Knowledge Assumed)",
        "",
        "Imagine you are running a popular food delivery app. On Friday evenings, traffic spikes",
        "10x. You need 50 servers. At 3am Sunday, you need 2 servers. Manually spinning servers",
        "up and down, restarting crashed apps, and distributing traffic is a full-time job.",
        "",
        "**Kubernetes (K8s) automates all of that.** It is an orchestration system that:",
        "- Runs your containerised apps across a cluster of machines",
        "- Automatically restarts crashed containers",
        "- Scales up (more containers) when traffic is high, scales down when quiet",
        "- Distributes traffic evenly across healthy containers",
        "- Rolls out new versions without downtime",
        "- Rolls back automatically if a new version is broken",
        "",
        "**Analogy:** Kubernetes is like the manager of a huge restaurant kitchen.",
        "You tell the manager: 'I need 5 chefs making pizza at all times.'",
        "The manager hires them, replaces any who quit, and adjusts staffing for rush hour —",
        "without you micromanaging each chef individually.",
        "",
        "```",
        "Without Kubernetes:                 With Kubernetes:",
        "  You manually SSH into servers       kubectl apply -f deployment.yaml",
        "  Restart crashed apps manually       K8s restarts crashed pods automatically",
        "  Scale servers by hand               K8s auto-scales based on CPU/memory",
        "  Roll out updates carefully          K8s does rolling updates (zero downtime)",
        "  Stay up at 3am for incidents        K8s self-heals 24/7",
        "```",
        "",
        "---",
        "",
        "## Cluster Architecture — The Big Picture",
        "",
        "A Kubernetes cluster has two types of machines:",
        "",
        "```",
        "+-------------------------------------------+",
        "|           CONTROL PLANE (Master)           |",
        "|                                           |",
        "|  +----------+  +---------+  +----------+ |",
        "|  | API       |  | Sched-  |  | etcd     | |",
        "|  | Server    |  | uler    |  | (cluster | |",
        "|  | (the hub) |  |         |  |  state)  | |",
        "|  +----------+  +---------+  +----------+ |",
        "|  +-----------+                            |",
        "|  | Controller|  (watches desired vs       |",
        "|  | Manager   |   actual state, fixes gaps)|",
        "|  +-----------+                            |",
        "+-------------------------------------------+",
        "         |            |            |",
        "   +-----+----+  +----+-----+  +--+-------+",
        "   |  WORKER  |  |  WORKER  |  |  WORKER  |",
        "   |  NODE 1  |  |  NODE 2  |  |  NODE 3  |",
        "   |          |  |          |  |          |",
        "   | [Pod][Pod|  | [Pod][Pod|  | [Pod]    |",
        "   |  kubelet |  |  kubelet |  |  kubelet |",
        "   |  kube-   |  |  kube-   |  |  kube-  |",
        "   |  proxy   |  |  proxy   |  |  proxy  |",
        "   +----------+  +----------+  +---------+",
        "",
        "Control Plane = the brain (decides what runs where)",
        "Worker Nodes  = the muscles (actually run your containers)",
        "```",
        "",
        "**Control Plane components:**",
        "- **API Server** — the front door. All kubectl commands hit this. `kubectl apply` talks to API Server.",
        "- **etcd** — a distributed key-value store. Stores ALL cluster state. If etcd is lost, the cluster is lost.",
        "- **Scheduler** — decides which worker node to place a new Pod on (based on resources, rules).",
        "- **Controller Manager** — watches actual vs desired state and fixes gaps (restarts crashed pods, etc.).",
        "",
        "**Worker Node components:**",
        "- **kubelet** — agent on each node. Receives instructions from API Server, starts/stops containers.",
        "- **kube-proxy** — handles networking rules so Pods can talk to each other and to Services.",
        "- **Container Runtime** — usually containerd (runs the actual containers, formerly Docker).",
        "",
        "---",
        "",
        "## Core Objects — The Building Blocks",
        "",
        "### Pod — The Smallest Unit",
        "",
        "```",
        "A Pod is one or more containers that:",
        "  - Share the same network namespace (same IP address)",
        "  - Share storage volumes",
        "  - Are always scheduled together on the same node",
        "",
        "+-----------------------------------+",
        "|              POD                  |",
        "|  +----------+  +---------------+ |",
        "|  | Main      |  | Sidecar       | |",
        "|  | Container |  | Container     | |",
        "|  | (app)     |  | (log shipper) | |",
        "|  +----------+  +---------------+ |",
        "|  Shared: IP address, volumes      |",
        "+-----------------------------------+",
        "",
        "99% of Pods contain just ONE container.",
        "Multi-container Pods are for tightly coupled helpers (sidecars).",
        "```",
        "",
        "**You almost never create Pods directly.** You create Deployments which manage Pods.",
        "",
        "### Deployment — Managing Replicas",
        "",
        "```yaml",
        "# deployment.yaml",
        "apiVersion: apps/v1",
        "kind: Deployment",
        "metadata:",
        "  name: my-app",
        "spec:",
        "  replicas: 3             # keep 3 Pods running at all times",
        "  selector:",
        "    matchLabels:",
        "      app: my-app",
        "  template:",
        "    metadata:",
        "      labels:",
        "        app: my-app       # Pods get this label",
        "    spec:",
        "      containers:",
        "        - name: my-app",
        "          image: myregistry/myapp:v1.2.3   # NEVER use :latest in production",
        "          ports:",
        "            - containerPort: 8080",
        "          resources:",
        "            requests:         # minimum guaranteed resources",
        "              cpu: '100m'     # 100 milliCPU = 0.1 CPU core",
        "              memory: '256Mi'",
        "            limits:           # maximum allowed",
        "              cpu: '500m'",
        "              memory: '512Mi'",
        "```",
        "",
        "```bash",
        "kubectl apply -f deployment.yaml    # create or update the deployment",
        "kubectl get deployments             # list deployments",
        "kubectl get pods                    # list pods",
        "kubectl describe deployment my-app  # detailed status",
        "kubectl rollout status deployment my-app  # watch rollout progress",
        "```",
        "",
        "### Service — Stable Network Access",
        "",
        "Pods are temporary — they die and restart with new IP addresses.",
        "A Service is a stable endpoint that always points to healthy Pods.",
        "",
        "```",
        "Client                Service                 Pods",
        "                     (stable IP/DNS)      (ephemeral IPs)",
        "",
        "browser -------> my-app-service -----> Pod 10.0.0.5",
        "  :80            10.96.0.100:80  \\---> Pod 10.0.0.8",
        "                                 \\---> Pod 10.0.0.12",
        "",
        "Even when Pods restart with new IPs, the Service IP stays the same.",
        "The Service load-balances across healthy Pods automatically.",
        "```",
        "",
        "```yaml",
        "# service.yaml",
        "apiVersion: v1",
        "kind: Service",
        "metadata:",
        "  name: my-app-service",
        "spec:",
        "  selector:",
        "    app: my-app          # routes traffic to Pods with label app=my-app",
        "  ports:",
        "    - port: 80           # Service port",
        "      targetPort: 8080   # Pod port",
        "  type: ClusterIP        # internal only (default)",
        "  # type: NodePort       # accessible on each node's IP:nodePort",
        "  # type: LoadBalancer   # creates a cloud load balancer (AWS ELB, GCP LB)",
        "```",
        "",
        "### ConfigMap and Secret",
        "",
        "```yaml",
        "# ConfigMap: non-sensitive config",
        "apiVersion: v1",
        "kind: ConfigMap",
        "metadata:",
        "  name: app-config",
        "data:",
        "  DATABASE_HOST: 'postgres-service'",
        "  LOG_LEVEL: 'INFO'",
        "",
        "# Secret: sensitive data (base64 encoded, use external secrets manager in prod)",
        "apiVersion: v1",
        "kind: Secret",
        "metadata:",
        "  name: app-secrets",
        "type: Opaque",
        "data:",
        "  DB_PASSWORD: c3VwZXJzZWNyZXQ=   # base64 of 'supersecret'",
        "```",
        "",
        "```yaml",
        "# Use in a Pod spec:",
        "env:",
        "  - name: DATABASE_HOST",
        "    valueFrom:",
        "      configMapKeyRef:",
        "        name: app-config",
        "        key: DATABASE_HOST",
        "  - name: DB_PASSWORD",
        "    valueFrom:",
        "      secretKeyRef:",
        "        name: app-secrets",
        "        key: DB_PASSWORD",
        "```",
        "",
        "---",
        "",
        "## kubectl — The Command Line Tool",
        "",
        "```bash",
        "# VIEWING RESOURCES",
        "kubectl get pods                         # list pods in current namespace",
        "kubectl get pods -n production           # list pods in 'production' namespace",
        "kubectl get pods -o wide                 # more detail (node, IP)",
        "kubectl get all                          # pods, services, deployments etc.",
        "kubectl describe pod my-pod-abc12        # detailed info including events (debug here!)",
        "",
        "# LOGS",
        "kubectl logs my-pod-abc12                # logs from a pod",
        "kubectl logs my-pod-abc12 -f             # follow live logs",
        "kubectl logs my-pod-abc12 --previous     # logs from crashed previous container",
        "",
        "# SHELL INTO A RUNNING POD",
        "kubectl exec -it my-pod-abc12 -- bash    # interactive shell (like docker exec)",
        "kubectl exec -it my-pod-abc12 -- sh      # use sh if bash not available",
        "",
        "# APPLY / DELETE",
        "kubectl apply -f deployment.yaml         # create or update resource",
        "kubectl delete -f deployment.yaml        # delete resource",
        "kubectl delete pod my-pod-abc12          # delete specific pod (Deployment restarts it)",
        "",
        "# SCALING",
        "kubectl scale deployment my-app --replicas=10  # scale to 10 pods",
        "",
        "# ROLLOUTS",
        "kubectl rollout status deployment my-app       # watch current rollout",
        "kubectl rollout history deployment my-app      # see revision history",
        "kubectl rollout undo deployment my-app         # roll back to previous version",
        "kubectl rollout undo deployment my-app --to-revision=3  # roll back to specific revision",
        "",
        "# PORT FORWARDING (debug locally)",
        "kubectl port-forward pod/my-pod-abc12 8080:8080  # access pod port locally",
        "kubectl port-forward service/my-app-service 8080:80",
        "",
        "# NAMESPACES",
        "kubectl get namespaces",
        "kubectl create namespace staging",
        "kubectl config set-context --current --namespace=staging  # set default namespace",
        "```",
        "",
        "---",
        "",
        "## Health Checks — Readiness vs Liveness Probes",
        "",
        "```",
        "Liveness Probe:   Is this container ALIVE? Should K8s restart it?",
        "Readiness Probe:  Is this container READY to receive traffic?",
        "",
        "Both are checked periodically by kubelet.",
        "",
        "LIVENESS failure  -> container killed and restarted",
        "READINESS failure -> container removed from Service endpoints (no traffic sent)",
        "                     but NOT restarted",
        "```",
        "",
        "```yaml",
        "livenessProbe:",
        "  httpGet:",
        "    path: /healthz    # your app must return 200 on this path",
        "    port: 8080",
        "  initialDelaySeconds: 30  # wait 30s before first check (app needs time to start)",
        "  periodSeconds: 10         # check every 10 seconds",
        "  failureThreshold: 3       # restart after 3 consecutive failures",
        "",
        "readinessProbe:",
        "  httpGet:",
        "    path: /ready      # return 200 when app is ready to serve traffic",
        "    port: 8080",
        "  initialDelaySeconds: 10",
        "  periodSeconds: 5",
        "  failureThreshold: 3",
        "```",
        "",
        "**Why both?**",
        "- App starts but crashes in a loop -> **liveness** probe detects -> K8s restarts.",
        "- App starts but DB connection not ready yet -> **readiness** probe returns 500 -> K8s holds",
        "  traffic until DB is connected -> then starts sending traffic. Zero dropped requests.",
        "",
        "---",
        "",
        "## Rolling Updates — Zero Downtime Deployments",
        "",
        "When you update an image tag in a Deployment, K8s rolls it out gradually:",
        "",
        "```",
        "Strategy: RollingUpdate (default)",
        "  maxUnavailable: 1   <- at most 1 pod down at a time",
        "  maxSurge: 1         <- at most 1 extra pod created during update",
        "",
        "Step 1:  [v1] [v1] [v1]       (3 old pods running)",
        "Step 2:  [v1] [v1] [v2]       (1 new pod started, readiness checked)",
        "Step 3:  [v1] [v2] [v2]       (1 old pod removed, 1 more new)",
        "Step 4:  [v2] [v2] [v2]       (rollout complete!)",
        "",
        "At every step, at least 2 pods are serving traffic.",
        "Traffic is only sent to pods that pass readiness probe.",
        "```",
        "",
        "```bash",
        "# Update image version (triggers rolling update)",
        "kubectl set image deployment/my-app my-app=myregistry/myapp:v1.3.0",
        "",
        "# Watch it happen",
        "kubectl rollout status deployment my-app",
        "",
        "# Something wrong? Roll back instantly",
        "kubectl rollout undo deployment my-app",
        "```",
        "",
        "---",
        "",
        "## Namespaces — Logical Isolation",
        "",
        "```",
        "Namespaces partition one cluster into virtual clusters.",
        "Use them to separate environments and teams.",
        "",
        "cluster/",
        "+-- namespace: default         (where things go if you don't specify)",
        "+-- namespace: kube-system     (K8s internal components)",
        "+-- namespace: production      (your prod workloads)",
        "+-- namespace: staging         (your staging workloads)",
        "+-- namespace: team-payments   (payments team's stuff)",
        "",
        "Benefits:",
        "  - Resource quotas per namespace (production gets more CPU budget)",
        "  - RBAC per namespace (staging team can't touch production)",
        "  - Clear separation, easier to manage",
        "```",
        "",
        "---",
        "",
        "## Resource Requests and Limits",
        "",
        "```",
        "requests: what the Pod is GUARANTEED to get (scheduler uses this to place Pod)",
        "limits:   maximum the Pod can USE (kernel enforces this)",
        "",
        "CPU:    measured in millicores. 1000m = 1 CPU core.",
        "Memory: measured in Mi (mebibytes) or Gi (gibibytes).",
        "",
        "If Pod exceeds memory LIMIT -> OOMKilled (Out Of Memory killed, then restarted)",
        "If Pod exceeds CPU LIMIT    -> throttled (slowed down, not killed)",
        "",
        "Best practice: set both requests and limits.",
        "requests too low  = Pod gets scheduled on overloaded node",
        "limits too low    = Pod OOMKilled frequently",
        "no limits at all  = one bad Pod can starve all others on the node",
        "```",
        "",
        "---",
        "",
        "## Ingress — HTTP Routing into the Cluster",
        "",
        "```",
        "Without Ingress:",
        "  Each Service needs its own LoadBalancer -> expensive (one cloud LB per service)",
        "",
        "With Ingress:",
        "  One LoadBalancer -> Ingress Controller -> routes to Services by host/path",
        "",
        "  External          Ingress            Services",
        "  Traffic    ->  Controller  ->  api.myapp.com  -> api-service",
        "                              ->  myapp.com/app -> frontend-service",
        "                              ->  myapp.com/pay -> payment-service",
        "```",
        "",
        "```yaml",
        "apiVersion: networking.k8s.io/v1",
        "kind: Ingress",
        "metadata:",
        "  name: my-ingress",
        "  annotations:",
        "    nginx.ingress.kubernetes.io/rewrite-target: /",
        "spec:",
        "  rules:",
        "    - host: myapp.com",
        "      http:",
        "        paths:",
        "          - path: /api",
        "            pathType: Prefix",
        "            backend:",
        "              service:",
        "                name: api-service",
        "                port:",
        "                  number: 80",
        "```",
        "",
        "---",
        "",
        "## Mind Map",
        "",
        "```",
        "KUBERNETES",
        "|",
        "+-- CLUSTER",
        "|   +-- Control Plane (API Server, etcd, Scheduler, Controller Manager)",
        "|   +-- Worker Nodes  (kubelet, kube-proxy, container runtime)",
        "|",
        "+-- CORE OBJECTS",
        "|   +-- Pod          (smallest unit: 1+ containers)",
        "|   +-- Deployment   (manages replicas + rolling updates)",
        "|   +-- Service      (stable network endpoint, load balancer)",
        "|   +-- ConfigMap    (non-sensitive config)",
        "|   +-- Secret       (sensitive config, base64 encoded)",
        "|   +-- Namespace    (logical cluster partition)",
        "|   +-- Ingress      (HTTP routing from outside)",
        "|",
        "+-- HEALTH",
        "|   +-- Liveness probe  (restart if dead)",
        "|   +-- Readiness probe (hold traffic if not ready)",
        "|",
        "+-- OPERATIONS (kubectl)",
        "|   +-- apply/delete     (create/remove resources)",
        "|   +-- get/describe     (view state)",
        "|   +-- logs/exec        (debug pods)",
        "|   +-- scale            (change replicas)",
        "|   +-- rollout undo     (rollback)",
        "|",
        "+-- RESOURCES",
        "    +-- requests (guaranteed minimum)",
        "    +-- limits   (enforced maximum)",
        "    +-- OOMKill  (memory limit breach)",
        "```",
        "",
        "---",
        "",
        "## How Kubernetes Connects to Other Topics",
        "",
        "- **Docker**: K8s runs Docker (or containerd) container images. Every app deployed to K8s",
        "  is a Docker image built and pushed to a registry.",
        "- **CI/CD**: Pipelines build images, push to registry, then `kubectl apply` to deploy.",
        "  GitOps tools (ArgoCD, Flux) watch git repos and auto-sync K8s state.",
        "- **Cloud/AWS**: AWS EKS is managed Kubernetes. GCP has GKE, Azure has AKS.",
        "  The control plane is managed for you — you only manage worker nodes.",
        "- **Linux**: Every K8s node is a Linux machine. When you `kubectl exec` into a pod,",
        "  you are in a Linux shell. Linux process/network skills apply.",
        "",
        "---",
        "",
        "## Common Beginner Mistakes",
        "",
        "1. **Using `image:latest`** — breaks reproducibility. Always pin: `myapp:v1.2.3`.",
        "2. **No resource requests/limits** — one runaway pod starves the entire node.",
        "3. **No readiness probe** — K8s sends traffic to pods before app is ready -> 502 errors during deploys.",
        "4. **Deleting pods to 'restart' them** — the correct way is `kubectl rollout restart deployment my-app`. Deleting pods in a Deployment just causes K8s to create new ones anyway.",
        "5. **Storing secrets in ConfigMaps** — ConfigMaps are not encrypted. Use Secrets (or better: External Secrets Operator + AWS Secrets Manager).",
        "6. **Everything in the default namespace** — use namespaces to separate environments and teams.",
        "7. **No liveness probe** — deadlocked pods keep running, serving no traffic, eating resources.",
        "",
        "---",
        "",
        "## References and Further Learning",
        "",
        "### Videos (Watch These!)",
        "- **Kubernetes Tutorial for Beginners** by TechWorld with Nana:",
        "  https://www.youtube.com/watch?v=X48VuDVv0do",
        "  - 4 hours. Complete K8s beginner course. Architecture, commands, real deployments.",
        "- **Kubernetes Explained in 100 Seconds** by Fireship:",
        "  https://www.youtube.com/watch?v=PziYflu8cB8",
        "  - 2 minutes. Perfect mental model overview.",
        "",
        "### Free Books and Articles",
        "- **Kubernetes official docs - Learn Kubernetes Basics interactive tutorial**:",
        "  https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        "  - Browser-based interactive minikube tutorial. No install needed.",
        "- **Kubernetes the Hard Way** by Kelsey Hightower:",
        "  https://github.com/kelseyhightower/kubernetes-the-hard-way",
        "  - Advanced: build K8s from scratch to truly understand it.",
        "",
        "### Diagrams and Cheatsheets",
        "- **kubectl cheatsheet (official)**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/",
        "- **Kubernetes architecture diagram**: search 'Kubernetes architecture diagram' — the official",
        "  CNCF diagram is the best visual reference.",
        "",
        "### Practice",
        "- **Killer Shell** (CKA/CKAD exam simulator): https://killer.sh/",
        "- **KodeKloud Kubernetes for Beginners** (browser labs, free tier):",
        "  https://kodekloud.com/courses/kubernetes-for-the-absolute-beginners-hands-on/",
        "- **Play with Kubernetes** (free browser K8s lab): https://labs.play-with-k8s.com/",
    ]

    K8S_GUIDE = "\n".join(lines)

    # ── QUESTIONS ──────────────────────────────────────────────────────────────────
    NEW_QUESTIONS = [
        {"id":"k8s-q4","type":"mcq",
         "prompt":"What is a Kubernetes Pod?",
         "choices":["A virtual machine","A physical server in a cluster","The smallest deployable unit — one or more containers sharing a network namespace and storage","A load balancer"],
         "answerIndex":2,"explanation":"A Pod is K8s smallest deployable unit. Containers in a Pod share an IP address and can share volumes. 99% of Pods contain a single container.","tags":["pods","k8s-basics"]},
        {"id":"k8s-q5","type":"mcq",
         "prompt":"What is the role of a Kubernetes Deployment?",
         "choices":["Handles HTTP routing","Stores cluster configuration","Declares desired state: how many Pod replicas to run, which image, rolling update strategy","Provides persistent storage"],
         "answerIndex":2,"explanation":"A Deployment manages a ReplicaSet which ensures the specified number of Pod replicas are always running. It also handles rolling updates and rollbacks.","tags":["deployment","k8s-core"]},
        {"id":"k8s-q6","type":"mcq",
         "prompt":"Why do Pods need a Service in front of them?",
         "choices":["Pods cannot run without a Service","Pods have dynamic IP addresses that change when they restart — a Service provides a stable IP/DNS name that always routes to healthy Pods","Services provide persistent storage","Services make Pods faster"],
         "answerIndex":1,"explanation":"When a Pod restarts, it gets a new IP address. A Service is a stable network endpoint with a fixed IP/DNS that automatically routes to current healthy Pods via label selectors.","tags":["services","networking"]},
        {"id":"k8s-q7","type":"mcq",
         "prompt":"What happens when a liveness probe fails repeatedly?",
         "choices":["The node is restarted","Traffic is stopped to the Pod","The container is killed and restarted by kubelet","The Deployment is deleted"],
         "answerIndex":2,"explanation":"Liveness probe failure = container is not alive/responsive. kubelet kills and restarts the container. This handles deadlocks and infinite loops that don't crash but stop responding.","tags":["probes","health"]},
        {"id":"k8s-q8","type":"mcq",
         "prompt":"A Pod passes its liveness probe but fails its readiness probe. What does Kubernetes do?",
         "choices":["Restarts the Pod","Deletes the Pod","Removes the Pod from the Service's endpoint list — no traffic is sent to it","Nothing — both probes must fail"],
         "answerIndex":2,"explanation":"Readiness failure means the container is alive but not ready for traffic. K8s removes it from Service endpoints. Traffic is only sent to ready Pods. The container is NOT restarted.","tags":["probes","readiness"]},
        {"id":"k8s-q9","type":"mcq",
         "prompt":"What does `kubectl rollout undo deployment my-app` do?",
         "choices":["Deletes the deployment","Scales the deployment to zero","Rolls back to the previous image version using Deployment revision history","Pauses the rollout"],
         "answerIndex":2,"explanation":"K8s Deployments keep a rollout history. rollout undo reverts to the previous revision — changing the image tag back and doing a rolling update in reverse. Fast and safe.","tags":["rollout","updates"]},
        {"id":"k8s-q10","type":"mcq",
         "prompt":"What is the difference between resource `requests` and `limits` in K8s?",
         "choices":["They are identical","requests = minimum guaranteed resources (scheduler uses to place Pod); limits = maximum allowed (enforced by kernel — OOMKill if exceeded)","requests = maximum; limits = minimum","limits only apply to CPU"],
         "answerIndex":1,"explanation":"requests guarantees the Pod gets at least that much CPU/memory. The scheduler uses requests to decide which node can fit the Pod. limits caps usage — memory overuse causes OOMKill; CPU overuse causes throttling.","tags":["resources","scheduling"]},
        {"id":"k8s-q11","type":"mcq",
         "prompt":"What does a Kubernetes Namespace provide?",
         "choices":["Network isolation between nodes","DNS resolution","Logical partitioning of cluster resources — lets different teams/environments share one cluster without interfering","Container image versioning"],
         "answerIndex":2,"explanation":"Namespaces partition a cluster logically. production and staging namespaces can coexist on the same cluster with separate resource quotas and RBAC policies.","tags":["namespaces","organization"]},
        {"id":"k8s-q12","type":"mcq",
         "prompt":"What is the role of `etcd` in the Kubernetes control plane?",
         "choices":["Schedules Pods to nodes","Runs containers","Distributed key-value store that holds ALL cluster state — the source of truth","Load balances services"],
         "answerIndex":2,"explanation":"etcd is K8s database. Every object (Pods, Deployments, Services, Secrets) is stored in etcd. If etcd is lost, the cluster state is lost. This is why etcd backups are critical.","tags":["control-plane","etcd"]},
        {"id":"k8s-q13","type":"mcq",
         "prompt":"You deploy a new image version and it is broken. Traffic is dropping. Fastest safe fix?",
         "choices":["kubectl delete deployment my-app and recreate","kubectl rollout undo deployment my-app","Manually edit each Pod","kubectl apply a ConfigMap change"],
         "answerIndex":1,"explanation":"kubectl rollout undo immediately reverts to the previous working revision using K8s rollout history. No downtime — it does a rolling update back to the old version.","tags":["rollout","incident-response"]},
        {"id":"k8s-q14","type":"mcq",
         "prompt":"What is the purpose of a Kubernetes Ingress?",
         "choices":["Internal pod-to-pod communication","Provides persistent volumes","Single entry point for HTTP/HTTPS traffic with host/path-based routing to multiple Services","Encrypts etcd data"],
         "answerIndex":2,"explanation":"Ingress routes external HTTP traffic to internal Services by hostname and path. Instead of one LoadBalancer per Service (expensive), one Ingress Controller handles all HTTP routing.","tags":["ingress","networking"]},
        {"id":"k8s-q15","type":"mcq",
         "prompt":"What is the difference between a ConfigMap and a Secret in Kubernetes?",
         "choices":["Secrets are bigger","ConfigMaps are for non-sensitive config (env vars, properties); Secrets are for sensitive data (passwords, tokens) and are base64-encoded","Secrets are encrypted at rest by default","They are identical"],
         "answerIndex":1,"explanation":"ConfigMaps store plain non-sensitive configuration. Secrets store sensitive data in base64 encoding (not encryption!). For true security, use external secrets managers (AWS Secrets Manager + External Secrets Operator).","tags":["configmap","secrets"]},
        {"id":"k8s-q16","type":"multi",
         "prompt":"Which kubectl commands are useful for debugging a crashing Pod? (Select all that apply)",
         "choices":["kubectl logs pod-name --previous","kubectl describe pod pod-name","kubectl exec -it pod-name -- bash","kubectl scale deployment my-app --replicas=0"],
         "answerIndexes":[0,1,2],"explanation":"logs --previous shows logs from the last crashed container. describe shows events and probe failures. exec drops you in for interactive debugging. Scaling to 0 just stops pods — not debugging.","tags":["debugging","kubectl"]},
        {"id":"k8s-q17","type":"mcq",
         "prompt":"Why is `image:latest` dangerous in Kubernetes production deployments?",
         "choices":["latest is not cached by Docker","latest tag makes rolling updates impossible","latest always pulls the newest version — a new image push could change your running app unpredictably, and K8s cannot tell old from new for rollout tracking","latest is not valid in K8s"],
         "answerIndex":2,"explanation":"If you use latest, any time K8s pulls the image it might get a different version. K8s also tracks rollout history by image digest — two 'latest' images may be different internally, breaking rollback.","tags":["best-practices","image-tags"]},
        {"id":"k8s-q18","type":"mcq",
         "prompt":"What does `kubectl port-forward pod/my-pod 8080:8080` do?",
         "choices":["Exposes the pod to the internet","Creates a temporary tunnel from your local port 8080 to port 8080 inside the pod — for local debugging","Changes the Service port","Scales the pod"],
         "answerIndex":1,"explanation":"port-forward creates a local tunnel directly to a Pod's port. You can access http://localhost:8080 and it tunnels to the Pod. No Service or Ingress needed. Great for debugging without exposing publicly.","tags":["kubectl","debugging"]},
        {"id":"k8s-q19","type":"mcq",
         "prompt":"In a rolling update with maxUnavailable=1 and maxSurge=1, starting from 3 replicas, what is the minimum number of Pods available during the update?",
         "choices":["0","1","2","3"],
         "answerIndex":2,"explanation":"maxUnavailable=1 means at most 1 pod can be down. Starting from 3, minimum available = 3-1 = 2. This ensures traffic continues flowing during the update.","tags":["rollout","availability"]},
        {"id":"k8s-q20","type":"mcq",
         "prompt":"What is kubelet's primary responsibility on a worker node?",
         "choices":["Routes external traffic","Stores cluster state","Watches the API Server for Pod assignments and ensures containers are running as specified on that node","Handles DNS resolution"],
         "answerIndex":2,"explanation":"kubelet is the K8s agent on each node. It watches the API Server for Pods assigned to its node, then starts/stops/restarts containers accordingly via the container runtime.","tags":["control-plane","kubelet"]},
    ]

    # ── FLASHCARDS ─────────────────────────────────────────────────────────────────
    NEW_FLASHCARDS = [
        {"id":"k8s-fc4","front":"Deployment vs Pod — when to create each","back":"Never create bare Pods in production. Always use Deployments. Deployments manage replicas, handle rolling updates, and restart crashed Pods automatically. Bare Pods are not restarted if they crash.","tags":["deployment","pods"]},
        {"id":"k8s-fc5","front":"Service types: ClusterIP / NodePort / LoadBalancer","back":"ClusterIP = internal only (default). NodePort = accessible on node IP:port (dev). LoadBalancer = creates cloud load balancer (production external traffic). Use Ingress + ClusterIP for HTTP at scale.","tags":["services","networking"]},
        {"id":"k8s-fc6","front":"OOMKilled — cause and fix","back":"Pod exceeded its memory LIMIT. Kubernetes kills and restarts it. Fix: increase memory limit, profile memory leak in code, or set limit closer to actual usage. CPU overuse = throttled (slowed), not killed.","tags":["resources","debugging"]},
        {"id":"k8s-fc7","front":"Rolling update safety rule","back":"Always set readiness probe. K8s only sends traffic to pods that pass readiness. Without it, pods get traffic before app is ready -> 502 errors. With it: seamless zero-downtime deploys.","tags":["rollout","probes"]},
        {"id":"k8s-fc8","front":"kubectl debug workflow","back":"1. kubectl get pods (find the pod name) 2. kubectl describe pod <name> (see events, probe failures) 3. kubectl logs <name> --previous (crashed container logs) 4. kubectl exec -it <name> -- bash (interactive debug)","tags":["debugging","kubectl"]},
    ]

    # ── WRITE ──────────────────────────────────────────────────────────────────────
    d['guide'] = K8S_GUIDE

    existing_q_ids = {q['id'] for q in d['questions']}
    for q in NEW_QUESTIONS:
        if q['id'] not in existing_q_ids:
            d['questions'].append(q)

    existing_fc_ids = {fc['id'] for fc in d['flashcards']}
    for fc in NEW_FLASHCARDS:
        if fc['id'] not in existing_fc_ids:
            d['flashcards'].append(fc)

    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

    print(f"kubernetes.json done!")
    print(f"  Guide: {len(K8S_GUIDE)} chars")
    print(f"  Questions: {len(d['questions'])}")
    print(f"  Flashcards: {len(d['flashcards'])}")
    print(f"  YouTube: {'youtube.com' in K8S_GUIDE}")
    print(f"  References: {'References' in K8S_GUIDE}")

    # ── patch_cicd.py ──────────────────────────────────────────────────────────────────
    p_cicd = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/cicd-pipelines.json')
    d_cicd = json.loads(p_cicd.read_text())

    CICD_GUIDE = "\n".join([
        "# CI/CD Pipelines",
        "",
        "## What Is CI/CD? (Start From Zero)",
        "",
        "Imagine baking a cake. The old way: bake the whole thing, put it in the oven for an hour,",
        "discover you forgot sugar — throw it away and start over. The new way: taste the batter",
        "at every step, catch mistakes early, ship a perfect cake every time.",
        "",
        "CI/CD does that for software. Without it, developers work in isolation for weeks,",
        "merge everything at once, and spend days fixing conflicts and broken builds.",
        "With CI/CD, every small change is automatically built, tested, and deployed —",
        "catching problems within minutes, not weeks.",
        "",
        "**CI = Continuous Integration**",
        "Every time a developer pushes code, an automated system:",
        "1. Pulls the latest code",
        "2. Builds it (compiles, packages)",
        "3. Runs all tests",
        "4. Reports pass/fail back to the developer in minutes",
        "",
        "**CD = Continuous Delivery / Continuous Deployment**",
        "- **Continuous Delivery**: code is ALWAYS in a deployable state. Deploy to production is a manual button click.",
        "- **Continuous Deployment**: every passing commit is AUTOMATICALLY deployed to production. No human click needed.",
        "",
        "```",
        "Developer pushes code",
        "        |",
        "        v",
        "  CI Server picks it up",
        "        |",
        "        v",
        "  Build (compile, package)",
        "        |",
        "        v",
        "  Run Tests (unit, integration, security scan)",
        "        |",
        "   Pass? |  Fail?",
        "        |         \\",
        "        v          v",
        "  Deploy to      Notify developer",
        "  Staging env    (email/Slack)",
        "        |",
        "        v",
        "  Run smoke tests",
        "        |",
        "        v",
        "  Deploy to Production",
        "  (auto or manual click)",
        "```",
        "",
        "---",
        "",
        "## CI vs CD vs CD — Clarified",
        "",
        "```",
        "+---------------------+---------------------------------------------------+",
        "| Term                | What it means                                     |",
        "+---------------------+---------------------------------------------------+",
        "| Continuous          | Merge small changes often (not once a month).     |",
        "| Integration (CI)    | Every merge triggers build + tests automatically. |",
        "+---------------------+---------------------------------------------------+",
        "| Continuous          | The pipeline always produces a deployable         |",
        "| Delivery (CD)       | artifact. Deployment to prod = manual trigger.    |",
        "+---------------------+---------------------------------------------------+",
        "| Continuous          | Every passing build is deployed to production     |",
        "| Deployment (CD)     | automatically. No human in the loop.              |",
        "+---------------------+---------------------------------------------------+",
        "",
        "Most companies use Continuous Delivery (manual prod deploy).",
        "High-trust orgs (Netflix, Amazon) use Continuous Deployment.",
        "```",
        "",
        "---",
        "",
        "## The Pipeline — Stage by Stage",
        "",
        "A pipeline is a series of automated stages. Each stage must pass before the next runs.",
        "",
        "```",
        "STAGE 1: SOURCE",
        "  Developer pushes to feature/my-feature branch",
        "  Opens Pull Request -> pipeline triggers",
        "",
        "STAGE 2: BUILD",
        "  Pull source code",
        "  Run: mvn package / npm run build / gradle build",
        "  Output: .jar / .war / Docker image",
        "  Fail here? -> build error (typo, missing import)",
        "",
        "STAGE 3: UNIT TESTS",
        "  Run: mvn test / npm test",
        "  Fast: thousands of tests in seconds",
        "  Fail here? -> logic bug, regression",
        "",
        "STAGE 4: STATIC ANALYSIS",
        "  Run: SonarQube / ESLint / Checkstyle",
        "  Checks: code quality, security vulnerabilities, style",
        "  Fail here? -> code smell, known CVE in dependency",
        "",
        "STAGE 5: BUILD DOCKER IMAGE",
        "  docker build -t myapp:${GIT_SHA} .",
        "  docker push registry/myapp:${GIT_SHA}",
        "  Tag with git commit SHA for traceability",
        "",
        "STAGE 6: DEPLOY TO STAGING",
        "  kubectl set image deployment/myapp myapp=registry/myapp:${GIT_SHA}",
        "  Wait for rollout to complete",
        "",
        "STAGE 7: INTEGRATION / E2E TESTS",
        "  Run against staging environment",
        "  Slower: tests real API calls, DB operations",
        "  Fail here? -> service interaction bug",
        "",
        "STAGE 8: DEPLOY TO PRODUCTION",
        "  Auto (Continuous Deployment) or manual approve button (Continuous Delivery)",
        "  Deployment strategy: rolling / blue-green / canary",
        "",
        "STAGE 9: POST-DEPLOY VERIFICATION",
        "  Smoke tests, health checks, error rate monitoring",
        "  Automatic rollback if error rate spikes",
        "```",
        "",
        "---",
        "",
        "## Popular CI/CD Tools",
        "",
        "```",
        "+------------------+--------------------------------------------------+",
        "| Tool             | What it is                                       |",
        "+------------------+--------------------------------------------------+",
        "| GitHub Actions   | Built into GitHub. YAML files in .github/        |",
        "|                  | workflows/. Free for public repos.               |",
        "+------------------+--------------------------------------------------+",
        "| GitLab CI/CD     | Built into GitLab. .gitlab-ci.yml in root.       |",
        "|                  | Powerful for self-hosted setups.                 |",
        "+------------------+--------------------------------------------------+",
        "| Jenkins          | Open-source, self-hosted. Very flexible,         |",
        "|                  | needs lots of config. Older but widely used.     |",
        "+------------------+--------------------------------------------------+",
        "| CircleCI         | Cloud-based. Fast parallel jobs.                 |",
        "+------------------+--------------------------------------------------+",
        "| AWS CodePipeline | Managed by AWS. Integrates with ECR, ECS, EKS.  |",
        "+------------------+--------------------------------------------------+",
        "| ArgoCD           | GitOps tool for Kubernetes. Watches git repo,    |",
        "|                  | auto-syncs K8s cluster state.                    |",
        "+------------------+--------------------------------------------------+",
        "```",
        "",
        "---",
        "",
        "## GitHub Actions — A Real Example",
        "",
        "GitHub Actions is the most common starting point. Pipelines are YAML files",
        "stored in `.github/workflows/` in your repo.",
        "",
        "```yaml",
        "# .github/workflows/ci.yml",
        "name: CI/CD Pipeline",
        "",
        "on:",
        "  push:",
        "    branches: [main, 'feature/**']  # trigger on push to main or feature branches",
        "  pull_request:",
        "    branches: [main]                # trigger on PRs to main",
        "",
        "jobs:",
        "  build-and-test:",
        "    runs-on: ubuntu-latest           # fresh Linux VM for each run",
        "",
        "    steps:",
        "      - name: Checkout code",
        "        uses: actions/checkout@v4    # clone the repo",
        "",
        "      - name: Set up Java 17",
        "        uses: actions/setup-java@v4",
        "        with:",
        "          java-version: '17'",
        "          distribution: 'temurin'",
        "",
        "      - name: Build with Maven",
        "        run: mvn -B package -DskipTests",
        "",
        "      - name: Run tests",
        "        run: mvn -B test",
        "",
        "      - name: Build Docker image",
        "        run: |",
        "          docker build -t myapp:${{ github.sha }} .",
        "          echo \"IMAGE_TAG=${{ github.sha }}\" >> $GITHUB_ENV",
        "",
        "  deploy-staging:",
        "    runs-on: ubuntu-latest",
        "    needs: build-and-test           # only runs if build-and-test passes",
        "    if: github.ref == 'refs/heads/main'  # only on main branch",
        "",
        "    steps:",
        "      - name: Deploy to staging",
        "        run: |",
        "          kubectl set image deployment/myapp \\",
        "            myapp=registry/myapp:${{ github.sha }}",
        "",
        "  deploy-production:",
        "    runs-on: ubuntu-latest",
        "    needs: deploy-staging",
        "    environment: production         # requires manual approval in GitHub UI",
        "",
        "    steps:",
        "      - name: Deploy to production",
        "        run: |",
        "          kubectl set image deployment/myapp \\",
        "            myapp=registry/myapp:${{ github.sha }}",
        "```",
        "",
        "**Key concepts in the YAML:**",
        "- `on:` — what triggers the pipeline (push, PR, schedule, manual)",
        "- `jobs:` — parallel or sequential units of work",
        "- `steps:` — individual commands within a job",
        "- `needs:` — job dependency (deploy only if build passed)",
        "- `environment: production` — requires manual approval gate",
        "- `github.sha` — the git commit hash, used to tag Docker images for traceability",
        "",
        "---",
        "",
        "## Deployment Strategies",
        "",
        "How you deploy new versions matters. Different strategies trade off risk vs speed.",
        "",
        "```",
        "ROLLING DEPLOYMENT (default in Kubernetes):",
        "  Replace old pods one by one with new ones.",
        "  At any moment, mix of old and new running.",
        "  Zero downtime. Rollback = kubectl rollout undo.",
        "",
        "  v1 v1 v1  ->  v1 v1 v2  ->  v1 v2 v2  ->  v2 v2 v2",
        "",
        "BLUE-GREEN DEPLOYMENT:",
        "  Run two identical environments: Blue (current) and Green (new).",
        "  Deploy new version to Green. Run full tests.",
        "  Switch load balancer from Blue to Green instantly.",
        "  Instant rollback: flip load balancer back to Blue.",
        "",
        "  Load Balancer ---> Blue (v1) [active]",
        "                 --> Green (v2) [idle, being tested]",
        "  Switch:",
        "  Load Balancer ---> Green (v2) [now active]",
        "                 --> Blue (v1) [idle, ready as rollback]",
        "",
        "CANARY DEPLOYMENT:",
        "  Send small % of traffic to new version. Observe metrics.",
        "  Gradually increase if healthy. Roll back if errors spike.",
        "",
        "  All users ---> v1  (95% traffic)",
        "            +--> v2  (5% traffic = 'canary')",
        "  If v2 metrics OK after 30 min:",
        "  All users ---> v1  (50%)",
        "            +--> v2  (50%)",
        "  ...continue until 100%",
        "",
        "RECREATE (simplest, has downtime):",
        "  Stop all v1 pods. Start all v2 pods.",
        "  Downtime = time between stop and start.",
        "  Only for non-critical, off-hours deployments.",
        "```",
        "",
        "---",
        "",
        "## Feature Flags",
        "",
        "Feature flags let you deploy code to production but keep it hidden behind a toggle.",
        "Deploy the code first, then enable the feature when ready — no new deployment needed.",
        "",
        "```",
        "// Code with feature flag",
        "if (featureFlags.isEnabled('new-checkout-flow', userId)) {",
        "    renderNewCheckout();",
        "} else {",
        "    renderOldCheckout();",
        "}",
        "",
        "Benefits:",
        "  - Deploy code without releasing features (decouple deploy from release)",
        "  - Enable for 1% of users first (like canary, but at code level)",
        "  - Instant kill switch: turn off broken feature in seconds",
        "  - A/B test: enable for group A, keep old for group B",
        "  - Enable for internal users first, then gradual rollout",
        "",
        "Tools: LaunchDarkly, AWS AppConfig, Unleash (open-source)",
        "```",
        "",
        "---",
        "",
        "## Artifacts and Image Registries",
        "",
        "```",
        "Artifact = the output of a build stage",
        "  Java: .jar or .war file",
        "  Node: bundled JS files",
        "  Docker: container image",
        "",
        "Image Registry = storage for Docker images",
        "  Docker Hub:     public registry (free for public images)",
        "  AWS ECR:        Amazon's private registry",
        "  GitHub CR:      ghcr.io — integrated with GitHub",
        "  GitLab Registry: built into GitLab",
        "",
        "Best practice: tag images with git commit SHA",
        "  myapp:latest              <- BAD: always moving, non-reproducible",
        "  myapp:a1b2c3d             <- GOOD: exact commit, reproducible",
        "  myapp:v1.2.3              <- GOOD: semantic version",
        "  myapp:main-20260428-a1b2  <- GOOD: branch + date + SHA",
        "",
        "Why SHA tag? You can trace any running container back to",
        "the exact git commit that produced it.",
        "```",
        "",
        "---",
        "",
        "## Secrets in CI/CD",
        "",
        "Pipelines need secrets: Docker registry credentials, K8s tokens, AWS keys.",
        "NEVER hardcode them in YAML files.",
        "",
        "```",
        "GitHub Actions: store in Settings -> Secrets and Variables -> Actions",
        "  Access in YAML: ${{ secrets.DOCKER_PASSWORD }}",
        "",
        "GitLab CI: Settings -> CI/CD -> Variables",
        "  Access in YAML: $DOCKER_PASSWORD",
        "",
        "Jenkins: Credentials Manager plugin",
        "  Reference in Jenkinsfile: credentials('my-docker-creds')",
        "",
        "Rule: secrets should NEVER appear in pipeline logs.",
        "CI tools auto-mask registered secrets.",
        "Use separate credentials per environment (staging creds != prod creds).",
        "```",
        "",
        "---",
        "",
        "## GitOps — The Modern Approach",
        "",
        "```",
        "Traditional CI/CD:                 GitOps:",
        "  Pipeline runs kubectl apply        Git repo = source of truth",
        "  Pipeline has cluster access        ArgoCD/Flux watches the repo",
        "  Manual cloud credentials           Detects drift, auto-syncs",
        "  Hard to audit changes              Every change = git commit",
        "                                     Full audit trail",
        "                                     Rollback = git revert",
        "",
        "GitOps flow:",
        "  Developer merges PR",
        "       |",
        "       v",
        "  CI pipeline builds + pushes image",
        "       |",
        "       v",
        "  Updates image tag in k8s manifests repo (separate git repo)",
        "       |",
        "       v",
        "  ArgoCD detects git change",
        "       |",
        "       v",
        "  ArgoCD syncs cluster to match git state",
        "```",
        "",
        "---",
        "",
        "## Mind Map",
        "",
        "```",
        "CI/CD PIPELINES",
        "|",
        "+-- CONCEPTS",
        "|   +-- CI = build + test on every push",
        "|   +-- Continuous Delivery = always deployable, manual prod",
        "|   +-- Continuous Deployment = auto deploy to prod",
        "|",
        "+-- PIPELINE STAGES",
        "|   +-- Source (git trigger)",
        "|   +-- Build (compile/package)",
        "|   +-- Test (unit -> integration -> E2E)",
        "|   +-- Security scan",
        "|   +-- Build Docker image",
        "|   +-- Deploy staging",
        "|   +-- Deploy production",
        "|",
        "+-- DEPLOYMENT STRATEGIES",
        "|   +-- Rolling (gradual, default K8s)",
        "|   +-- Blue-Green (instant switch, easy rollback)",
        "|   +-- Canary (% traffic to new version)",
        "|   +-- Recreate (downtime, avoid in prod)",
        "|",
        "+-- TOOLS",
        "|   +-- GitHub Actions (.github/workflows/*.yml)",
        "|   +-- GitLab CI (.gitlab-ci.yml)",
        "|   +-- Jenkins (Jenkinsfile)",
        "|   +-- ArgoCD (GitOps for K8s)",
        "|",
        "+-- BEST PRACTICES",
        "    +-- Tag images with git SHA",
        "    +-- Secrets via vault/CI secrets, never in YAML",
        "    +-- Fail fast: put fastest tests first",
        "    +-- Feature flags for safe rollouts",
        "```",
        "",
        "---",
        "",
        "## How CI/CD Connects to Other Topics",
        "",
        "- **Git**: Every pipeline is triggered by a git event (push, merge). Your branching",
        "  strategy (GitHub Flow) directly shapes your pipeline design.",
        "- **Docker**: Pipelines build Docker images and push them to registries.",
        "- **Kubernetes**: Pipelines deploy to K8s clusters via kubectl or ArgoCD.",
        "- **Linux**: Pipeline steps run bash scripts on Linux runners.",
        "",
        "---",
        "",
        "## Common Beginner Mistakes",
        "",
        "1. **Secrets in YAML files** — anyone who reads the pipeline file sees your AWS key.",
        "2. **Too many manual steps** — the value of CI/CD comes from automation. Manual = slow.",
        "3. **No staging environment** — deploying untested code straight to production.",
        "4. **Monolithic pipeline** — one giant job. Split into parallel jobs for speed.",
        "5. **Not pinning Action versions** — `uses: actions/checkout@main` can change unexpectedly. Pin: `@v4`.",
        "6. **Slow tests blocking pipeline** — run unit tests first (fast), integration tests last (slow). Fail fast.",
        "7. **Using `latest` image tag** — makes deployments non-reproducible. Use git SHA.",
        "",
        "---",
        "",
        "## References and Further Learning",
        "",
        "### Videos (Watch These!)",
        "- **GitHub Actions Tutorial - Basic Concepts and CI/CD Pipeline** by TechWorld with Nana:",
        "  https://www.youtube.com/watch?v=R8_veQiYBjI",
        "  - 32 minutes. Clear GitHub Actions walkthrough from scratch.",
        "- **CI/CD Explained in 100 Seconds** by Fireship:",
        "  https://www.youtube.com/watch?v=scEDHsr3APg",
        "  - 2 minutes. Perfect high-level overview.",
        "",
        "### Free Books and Articles",
        "- **GitHub Actions official docs**: https://docs.github.com/en/actions",
        "  - 'Quickstart for GitHub Actions' is the best starting point.",
        "- **Google's DevOps Research (DORA metrics)**: https://dora.dev/",
        "  - The research behind why CI/CD matters. Understand deploy frequency and lead time.",
        "",
        "### Diagrams and Cheatsheets",
        "- **GitHub Actions Cheatsheet**: https://github.github.io/actions-cheat-sheet/actions-cheat-sheet.html",
        "- **Blue-Green vs Canary diagram**: search 'deployment strategies comparison diagram'",
        "",
        "### Practice",
        "- **GitHub Actions Starter Workflows**: https://github.com/actions/starter-workflows",
        "  - Official templates for Java, Node, Docker, K8s — start from a working example.",
        "- **KodeKloud CI/CD with GitHub Actions** (free tier):",
        "  https://kodekloud.com/courses/github-actions/",
    ])

    CICD_NEW_Q = [
        {"id":"cicd-q4","type":"mcq","prompt":"What is the primary purpose of Continuous Integration (CI)?",
         "choices":["Automatically deploy to production","Merge and test code changes automatically on every push, catching bugs early",
                    "Monitor production systems","Manage cloud infrastructure"],
         "answerIndex":1,"explanation":"CI ensures every code push triggers an automated build and test run. Bugs are caught within minutes of introduction, not discovered weeks later during a big merge.","tags":["ci","pipeline"]},
        {"id":"cicd-q5","type":"mcq","prompt":"In a GitHub Actions workflow, what does `needs: build-and-test` do on a deploy job?",
         "choices":["Runs the deploy job in parallel with build-and-test","Runs build-and-test after deploy","Prevents deploy from running unless build-and-test job passed","Skips build-and-test"],
         "answerIndex":2,"explanation":"needs creates a dependency. The deploy job waits for build-and-test to complete successfully. If build-and-test fails, deploy is skipped entirely.","tags":["github-actions","pipeline"]},
        {"id":"cicd-q6","type":"mcq","prompt":"What deployment strategy allows instant rollback by switching a load balancer?",
         "choices":["Rolling deployment","Recreate deployment","Blue-Green deployment","Canary deployment"],
         "answerIndex":2,"explanation":"Blue-Green keeps two identical environments. Rollback is instant — just flip the load balancer back to the old (Blue) environment. No pod restarts, no downtime.","tags":["deployment-strategies","blue-green"]},
        {"id":"cicd-q7","type":"mcq","prompt":"A canary deployment sends 5% of traffic to the new version. Why not 100% immediately?",
         "choices":["The registry can only handle 5%","To limit blast radius — if the new version has bugs, only 5% of users are affected while you monitor metrics before full rollout",
                    "Kubernetes requires this","It is cheaper"],
         "answerIndex":1,"explanation":"Canary limits risk. You observe error rates, latency, and business metrics on the 5% canary. If metrics stay healthy, gradually increase. If they spike, roll back — only 5% of users experienced the bug.","tags":["deployment-strategies","canary"]},
        {"id":"cicd-q8","type":"mcq","prompt":"Why should Docker images be tagged with the git commit SHA rather than `latest`?",
         "choices":["SHA tags are smaller","latest is not valid in CI","SHA creates a permanent, traceable link between a running container and the exact code commit that produced it — enabling reproducibility and rollback",
                    "SHA tags deploy faster"],
         "answerIndex":2,"explanation":"myapp:latest changes over time. myapp:a1b2c3d is permanent. You can trace a production issue to the exact commit, reproduce the exact environment, and roll back to a specific previous SHA.","tags":["artifacts","best-practices"]},
        {"id":"cicd-q9","type":"mcq","prompt":"What is the key difference between Continuous Delivery and Continuous Deployment?",
         "choices":["They are the same","Continuous Delivery deploys automatically; Continuous Deployment requires manual approval",
                    "Continuous Delivery requires manual approval for production; Continuous Deployment deploys automatically on every passing build",
                    "Continuous Deployment only works with Kubernetes"],
         "answerIndex":2,"explanation":"Continuous Delivery: pipeline produces a deployable artifact. Deployment to production needs a human to click approve. Continuous Deployment: no human — every passing build goes straight to production.","tags":["cd","pipeline"]},
        {"id":"cicd-q10","type":"mcq","prompt":"Where should CI/CD pipeline secrets (Docker credentials, AWS keys) be stored?",
         "choices":["In the .yml workflow file (base64 encoded)","In a .env file committed to git","In the CI platform's secret store (GitHub Secrets, GitLab Variables, Jenkins Credentials)","In a README comment"],
         "answerIndex":2,"explanation":"CI platforms have built-in encrypted secret stores. Secrets are injected as environment variables at runtime — never visible in logs or source code. Never commit secrets to git.","tags":["security","secrets"]},
        {"id":"cicd-q11","type":"mcq","prompt":"What does a feature flag let you do that a standard deployment does not?",
         "choices":["Deploy faster","Deploy code to production without activating the feature — and enable it for specific users/% without redeploying",
                    "Skip testing","Deploy multiple services at once"],
         "answerIndex":1,"explanation":"Feature flags decouple deploy from release. Code is deployed but hidden. You can enable for 1% of users, monitor, then roll out gradually. Instant kill switch: just toggle off. No new deployment needed.","tags":["feature-flags","deployment"]},
        {"id":"cicd-q12","type":"mcq","prompt":"In a pipeline, why should unit tests run BEFORE integration tests?",
         "choices":["Unit tests are more important","Unit tests are fast (seconds) and catch logic bugs early — fail fast principle. Integration tests are slow (minutes). No point running slow tests if fast ones already failed.",
                    "Integration tests require unit tests to pass first","It is a GitLab requirement"],
         "answerIndex":1,"explanation":"Fail fast: run cheapest, fastest checks first. Unit tests run in seconds. If a unit test fails, skip the 10-minute integration test suite. This gives developers faster feedback and saves CI compute time.","tags":["pipeline","testing"]},
        {"id":"cicd-q13","type":"mcq","prompt":"What is GitOps?",
         "choices":["Using git for code reviews only","A git branching strategy","A practice where git is the single source of truth for infrastructure state — tools like ArgoCD watch git and auto-sync the cluster to match",
                    "A type of deployment strategy"],
         "answerIndex":2,"explanation":"GitOps: every change to infrastructure goes through a git commit. ArgoCD watches the git repo and makes Kubernetes match it. Full audit trail, rollback = git revert, no manual kubectl from pipelines.","tags":["gitops","kubernetes"]},
        {"id":"cicd-q14","type":"mcq","prompt":"A rolling deployment and a recreate deployment both deploy a new version. Key difference?",
         "choices":["Rolling is faster","Recreate works only on Kubernetes","Rolling replaces pods gradually (zero downtime); Recreate stops all old pods then starts new ones (has downtime)",
                    "They are identical"],
         "answerIndex":2,"explanation":"Rolling: at every step some pods serve traffic — no downtime. Recreate: all old pods stop, then new pods start — gap = downtime. Use rolling or blue-green in production.","tags":["deployment-strategies","rolling"]},
        {"id":"cicd-q15","type":"mcq","prompt":"What is the `environment: production` key in GitHub Actions used for?",
         "choices":["Sets environment variables","Specifies which OS to use","Creates a manual approval gate — the job waits for a reviewer to approve before running",
                    "Points to a production .env file"],
         "answerIndex":2,"explanation":"GitHub Environments let you require manual reviewers before a job runs. Useful for production deploys: CI auto-deploys to staging, but production requires a human to approve in GitHub UI.","tags":["github-actions","approval"]},
        {"id":"cicd-q16","type":"mcq","prompt":"What is a pipeline artifact?",
         "choices":["A test failure report","The output of a build stage (compiled .jar, Docker image, test reports) passed to subsequent stages","A git branch","A deployment strategy"],
         "answerIndex":1,"explanation":"Artifacts are the build outputs: compiled binaries, Docker images, test coverage reports. They are stored and passed between pipeline stages. The Docker image produced in build is deployed in the deploy stage.","tags":["artifacts","pipeline"]},
        {"id":"cicd-q17","type":"multi","prompt":"Which are valid triggers for a GitHub Actions workflow? (Select all that apply)",
         "choices":["push to a branch","pull_request opened","schedule (cron)","manual workflow_dispatch"],
         "answerIndexes":[0,1,2,3],"explanation":"GitHub Actions supports: push (on code push), pull_request (PR events), schedule (cron-like), workflow_dispatch (manual trigger from UI), and many more. All four listed are valid.","tags":["github-actions","triggers"]},
        {"id":"cicd-q18","type":"mcq","prompt":"What DORA metric measures how often a team deploys to production?",
         "choices":["Mean Time to Recovery","Change Failure Rate","Lead Time for Changes","Deployment Frequency"],
         "answerIndex":3,"explanation":"DORA (DevOps Research and Assessment) defines 4 metrics: Deployment Frequency, Lead Time for Changes, Mean Time to Recovery (MTTR), and Change Failure Rate. Deployment Frequency = how often you ship.","tags":["dora","metrics"]},
        {"id":"cicd-q19","type":"mcq","prompt":"Why should you pin GitHub Action versions (`uses: actions/checkout@v4`) instead of using `@main`?",
         "choices":["v4 is faster","@main is invalid","@main always uses the newest version which may have breaking changes. @v4 is a locked version — your pipeline is reproducible and safe from unexpected upstream changes.",
                    "It is a git requirement"],
         "answerIndex":2,"explanation":"Third-party actions should be pinned. actions/checkout@main could change any day. @v4 is stable. Better practice: pin to exact SHA (actions/checkout@abc1234) for maximum security.","tags":["github-actions","best-practices"]},
        {"id":"cicd-q20","type":"mcq","prompt":"What is the blast radius of a bug in continuous deployment vs continuous delivery?",
         "choices":["Identical — the bug is in prod either way","Continuous Deployment can affect all users immediately (auto-deployed). Continuous Delivery gives humans a chance to catch issues before approving the production deploy.",
                    "Continuous Delivery has larger blast radius","Blast radius depends only on test coverage"],
         "answerIndex":1,"explanation":"With Continuous Deployment, a bug that passes tests reaches all production users automatically. With Continuous Delivery, a human reviews before prod — potential extra safety net. Both still require good test coverage.","tags":["cd","risk"]},
    ]

    CICD_NEW_FC = [
        {"id":"cicd-fc4","front":"CI pipeline stage order (fail-fast)","back":"Source -> Build -> Unit Tests (fast) -> Static Analysis -> Build Image -> Deploy Staging -> Integration Tests (slow) -> Deploy Prod. Put fastest checks first to fail fast and save compute.","tags":["ci","pipeline"]},
        {"id":"cicd-fc5","front":"Rolling vs Blue-Green vs Canary","back":"Rolling: replace pods gradually, zero downtime. Blue-Green: two envs, instant LB switch, easy rollback. Canary: % traffic to new version, gradual increase. Recreate: all-stop then all-start (has downtime, avoid).","tags":["deployment-strategies"]},
        {"id":"cicd-fc6","front":"Feature flag vs new deployment","back":"Feature flag: code in prod but toggled off. Enable per user/% without redeploying. Kill switch in seconds. Deploy = code change. Feature flag = behaviour change. Decouple both.","tags":["feature-flags"]},
        {"id":"cicd-fc7","front":"GitOps in one sentence","back":"Git repo is the source of truth for infrastructure state. ArgoCD/Flux watches git and auto-syncs Kubernetes. Every change is a git commit. Rollback = git revert. Full audit trail.","tags":["gitops"]},
        {"id":"cicd-fc8","front":"CI/CD secrets rule","back":"Store in CI secret store (GitHub Secrets/GitLab Variables). Reference as ${{ secrets.KEY }}. Never in YAML files, never in git. Use separate credentials per environment. CI platforms auto-mask secrets in logs.","tags":["security","secrets"]},
    ]

    d_cicd['guide'] = CICD_GUIDE
    qids = {q['id'] for q in d_cicd['questions']}
    for q in CICD_NEW_Q:
        if q['id'] not in qids:
            d_cicd['questions'].append(q)
    fcids = {f['id'] for f in d_cicd['flashcards']}
    for fc in CICD_NEW_FC:
        if fc['id'] not in fcids:
            d_cicd['flashcards'].append(fc)
    with open(p_cicd, 'w') as f:
        json.dump(d_cicd, f, indent=2, ensure_ascii=False)
    print(f"cicd-pipelines.json done: guide={len(CICD_GUIDE)} q={len(d_cicd['questions'])} fc={len(d_cicd['flashcards'])}")

    # ── patch_cloud.py ──────────────────────────────────────────────────────────────────
    p_cloud = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/cloud-fundamentals.json')
    d_cloud = json.loads(p_cloud.read_text())

    CLOUD_GUIDE = "\n".join([
        "# Cloud Fundamentals",
        "",
        "## What Is Cloud Computing? (Start From Zero)",
        "",
        "Before cloud computing, if you wanted to run a website, you had to:",
        "1. Buy physical servers (thousands of dollars)",
        "2. Find a data centre to put them in (expensive rent)",
        "3. Hire someone to maintain them 24/7",
        "4. Guess how much traffic you would get and buy enough hardware upfront",
        "5. Wait weeks for the hardware to arrive and be set up",
        "",
        "If your website suddenly became popular, you were stuck — more hardware took weeks.",
        "If traffic was low, your expensive servers sat idle wasting money.",
        "",
        "**Cloud computing flips this model.** You rent computing resources (servers, storage,",
        "databases) from a cloud provider (AWS, Google Cloud, Azure) over the internet.",
        "You pay only for what you use, scale up or down in minutes, and never touch hardware.",
        "",
        "**Analogy:** Think of electricity. You do not build your own power plant to get electricity.",
        "You plug into the grid, use what you need, and pay the bill. Cloud computing is the",
        "same idea for servers, storage, and software infrastructure.",
        "",
        "```",
        "Before cloud:                          After cloud:",
        "  Buy servers = $50,000 upfront          Pay $0.02/hour per server",
        "  Setup time = 4-8 weeks                 Setup time = 2 minutes",
        "  Traffic spike = site goes down         Traffic spike = auto-scale in seconds",
        "  Low traffic = wasted hardware          Low traffic = scale to zero, pay nothing",
        "  Hardware failure = your problem        Hardware failure = provider's problem",
        "```",
        "",
        "---",
        "",
        "## The Three Main Cloud Providers",
        "",
        "```",
        "+----------+-----------------------------------------------------------+",
        "| Provider | Key facts                                                 |",
        "+----------+-----------------------------------------------------------+",
        "| AWS      | Amazon Web Services. Largest market share (31%).         |",
        "| (Amazon) | Most services, most mature. EC2, S3, Lambda, RDS, EKS.  |",
        "+----------+-----------------------------------------------------------+",
        "| Azure    | Microsoft Azure. Strong in enterprise/Windows shops.      |",
        "| (MS)     | AKS (K8s), Active Directory integration, Office365.      |",
        "+----------+-----------------------------------------------------------+",
        "| GCP      | Google Cloud Platform. Strongest in ML/AI, BigQuery.     |",
        "| (Google) | GKE (K8s), BigQuery, Vertex AI, Cloud Run.              |",
        "+----------+-----------------------------------------------------------+",
        "",
        "All three offer similar services under different names.",
        "AWS: EC2  |  Azure: Virtual Machines  |  GCP: Compute Engine",
        "AWS: S3   |  Azure: Blob Storage      |  GCP: Cloud Storage",
        "AWS: RDS  |  Azure: Azure SQL         |  GCP: Cloud SQL",
        "```",
        "",
        "---",
        "",
        "## Service Models — IaaS, PaaS, SaaS, FaaS",
        "",
        "Cloud services come in layers — each layer abstracts away more complexity.",
        "The higher up you go, the less you manage.",
        "",
        "```",
        "ON-PREMISES (you manage everything):",
        "  Hardware, Network, Storage, Virtualization,",
        "  OS, Runtime, Middleware, Applications, Data",
        "  You manage: EVERYTHING",
        "",
        "IAAS (Infrastructure as a Service):",
        "  Cloud manages: Hardware, Network, Storage, Virtualization",
        "  You manage:    OS, Runtime, Middleware, Applications, Data",
        "  Examples:      AWS EC2, Azure VMs, Google Compute Engine",
        "  Use when:      Need full control over OS and runtime",
        "",
        "PAAS (Platform as a Service):",
        "  Cloud manages: Hardware, Network, Storage, Virtualization, OS, Runtime",
        "  You manage:    Applications, Data",
        "  Examples:      AWS Elastic Beanstalk, Heroku, Google App Engine",
        "  Use when:      Just want to deploy code without managing servers",
        "",
        "SAAS (Software as a Service):",
        "  Cloud manages: EVERYTHING",
        "  You manage:    Just use the application",
        "  Examples:      Gmail, Slack, Salesforce, GitHub",
        "  Use when:      End-user product — no infrastructure responsibility",
        "",
        "FAAS (Function as a Service / Serverless):",
        "  Cloud manages: Hardware, OS, Runtime, Scaling",
        "  You provide:   A function (code snippet)",
        "  You pay for:   Execution time only (milliseconds)",
        "  Examples:      AWS Lambda, Google Cloud Functions, Azure Functions",
        "  Use when:      Event-driven, sporadic workloads",
        "```",
        "",
        "**Analogy — pizza:**",
        "```",
        "On-premises = make pizza at home (buy ingredients, oven, everything yourself)",
        "IaaS         = use a restaurant kitchen (they provide oven + space, you cook)",
        "PaaS         = pizza delivery kit (they provide dough+sauce, you just add toppings)",
        "SaaS         = order pizza delivery (someone else does everything, you just eat)",
        "FaaS         = pay per slice eaten (only pay when you consume something)",
        "```",
        "",
        "---",
        "",
        "## Regions and Availability Zones",
        "",
        "Cloud providers divide the world into geographic areas to provide low latency",
        "and fault tolerance.",
        "",
        "```",
        "REGION = a geographic area with multiple data centres",
        "  Examples: us-east-1 (N. Virginia), eu-west-1 (Ireland), ap-southeast-1 (Singapore)",
        "  AWS has 30+ regions globally.",
        "  You choose a region close to your users for low latency.",
        "",
        "AVAILABILITY ZONE (AZ) = one or more physical data centres within a region",
        "  Each region has 2-6 AZs.",
        "  AZs are physically separated (different buildings, different power/network)",
        "  but connected with high-speed private fibre.",
        "",
        "  us-east-1",
        "  +-------------------------------------------------------+",
        "  |  AZ: us-east-1a    AZ: us-east-1b    AZ: us-east-1c  |",
        "  |  Data centre 1     Data centre 2     Data centre 3    |",
        "  +-------------------------------------------------------+",
        "",
        "MULTI-AZ = deploy your app in multiple AZs simultaneously",
        "  If one AZ has a power outage, your app keeps running in the others.",
        "  Load balancer distributes traffic across all healthy AZs.",
        "",
        "Why not one big data centre?",
        "  Single point of failure: one storm, power outage, or fire takes everything down.",
        "  Multi-AZ = high availability (HA).",
        "```",
        "",
        "**Key distinction:**",
        "```",
        "Region failure: entire geographic area down (rare, major disaster)",
        "AZ failure:     one data centre down (more common: power, hardware)",
        "",
        "Best practice for production:",
        "  Deploy across at least 2 AZs in one region.",
        "  For true disaster recovery: active-active across 2 regions.",
        "```",
        "",
        "---",
        "",
        "## Core Cloud Networking",
        "",
        "```",
        "VPC (Virtual Private Cloud) = your private network in the cloud",
        "  Isolated network just for your account.",
        "  You define IP address ranges, subnets, routing rules.",
        "",
        "  +--------------------------------------------------+",
        "  |                VPC: 10.0.0.0/16                  |",
        "  |                                                  |",
        "  |  Public Subnet         Private Subnet            |",
        "  |  10.0.1.0/24           10.0.2.0/24               |",
        "  |  (Internet accessible) (No direct internet)      |",
        "  |  [Load Balancer]       [App Servers]             |",
        "  |  [Bastion Host]        [Databases]               |",
        "  +--+-----------------------------------------------+",
        "     |",
        "  Internet Gateway -> connects VPC to internet",
        "",
        "PUBLIC SUBNET: resources have public IPs, reachable from internet",
        "  Use for: load balancers, bastion hosts, NAT gateways",
        "",
        "PRIVATE SUBNET: no public IPs, not directly reachable from internet",
        "  Use for: app servers, databases, internal services",
        "  Can reach internet via NAT Gateway (outbound only)",
        "",
        "Security Groups = stateful firewall for EC2/RDS instances",
        "  Rule: ALLOW port 443 from 0.0.0.0/0 (any IP)",
        "  Rule: ALLOW port 5432 from 10.0.0.0/16 (VPC only)",
        "",
        "NACLs = stateless firewall at subnet level",
        "```",
        "",
        "---",
        "",
        "## IAM — Identity and Access Management",
        "",
        "IAM controls WHO can do WHAT in your cloud account.",
        "This is arguably the most important security concept in cloud.",
        "",
        "```",
        "IAM concepts:",
        "",
        "USER:    A person or service that interacts with AWS",
        "         Has credentials (password for console, access key for API)",
        "",
        "GROUP:   Collection of users with shared permissions",
        "         e.g. 'developers' group has read-only prod, full dev access",
        "",
        "ROLE:    An identity assumed by a service or user temporarily",
        "         EC2 instance assumes role 'app-role' to read from S3",
        "         No hardcoded credentials needed!",
        "",
        "POLICY:  JSON document defining allowed/denied actions",
        "         Attached to users, groups, or roles",
        "",
        "Example policy (S3 read-only):",
        "{",
        "  'Effect': 'Allow',",
        "  'Action': ['s3:GetObject', 's3:ListBucket'],",
        "  'Resource': 'arn:aws:s3:::my-bucket/*'",
        "}",
        "```",
        "",
        "**Principle of Least Privilege:**",
        "```",
        "Give every identity the MINIMUM permissions it needs — nothing more.",
        "",
        "Bad:  EC2 instance has AdministratorAccess policy",
        "      -> if compromised, attacker controls your entire AWS account",
        "",
        "Good: EC2 instance has a role allowing ONLY:",
        "      - s3:GetObject on the specific bucket it needs",
        "      - secretsmanager:GetSecretValue for its DB password",
        "",
        "Use IAM roles for EC2/Lambda/ECS — NEVER use access keys on servers.",
        "Access keys can be stolen. Roles are automatically rotated by AWS.",
        "```",
        "",
        "---",
        "",
        "## Cloud Pricing Models",
        "",
        "```",
        "ON-DEMAND:",
        "  Pay per second/hour you use.",
        "  No commitment. Most flexible. Most expensive per hour.",
        "  Use for: unpredictable workloads, short-term needs.",
        "",
        "RESERVED INSTANCES:",
        "  Commit to 1 or 3 years. Pay upfront or monthly.",
        "  Up to 72% cheaper than on-demand.",
        "  Use for: steady, predictable workloads (production databases).",
        "",
        "SPOT INSTANCES (AWS-specific):",
        "  Bid on spare AWS capacity. Up to 90% cheaper than on-demand.",
        "  AWS can reclaim with 2-minute notice.",
        "  Use for: batch jobs, ML training, fault-tolerant workloads.",
        "  NOT for: databases, anything that cannot handle interruption.",
        "",
        "SAVINGS PLANS:",
        "  Commit to a dollar amount of compute per hour for 1-3 years.",
        "  More flexible than Reserved Instances.",
        "  Applies across services (EC2, Lambda, Fargate).",
        "",
        "FREE TIER:",
        "  AWS, GCP, Azure all have free tiers for learning.",
        "  AWS: 750 hours EC2 t2.micro/month for 12 months.",
        "  AWS: 5GB S3 storage forever.",
        "  AWS Lambda: 1 million requests/month forever.",
        "```",
        "",
        "---",
        "",
        "## Key Cloud Services Quick Reference",
        "",
        "```",
        "COMPUTE:",
        "  EC2          = virtual machine (you manage OS, patches)",
        "  Lambda       = serverless function (you just write code)",
        "  ECS/EKS      = run Docker containers / Kubernetes",
        "  Fargate      = serverless containers (no EC2 to manage)",
        "",
        "STORAGE:",
        "  S3           = object storage (files, images, backups, static sites)",
        "  EBS          = block storage (like a hard drive, attached to EC2)",
        "  EFS          = shared filesystem (multiple EC2s mount same volume)",
        "",
        "DATABASE:",
        "  RDS          = managed relational DB (MySQL, PostgreSQL, etc.)",
        "  DynamoDB     = NoSQL, serverless, millisecond latency",
        "  ElastiCache  = managed Redis/Memcached (caching)",
        "",
        "NETWORKING:",
        "  VPC          = private network",
        "  Route 53     = DNS service",
        "  CloudFront   = CDN (cache content close to users globally)",
        "  ELB/ALB      = load balancer",
        "",
        "SECURITY:",
        "  IAM          = identity and access control",
        "  KMS          = encryption key management",
        "  WAF          = web application firewall",
        "",
        "DEVOPS:",
        "  CloudWatch   = monitoring, logs, alerts",
        "  CloudFormation = infrastructure as code (YAML/JSON templates)",
        "  CDK          = CloudFormation but in real code (TypeScript/Python)",
        "  CodePipeline = AWS-native CI/CD",
        "```",
        "",
        "---",
        "",
        "## The Shared Responsibility Model",
        "",
        "```",
        "Cloud security is a shared responsibility between you and the provider.",
        "",
        "Cloud provider responsible for:     You are responsible for:",
        "  Physical hardware security          Your application code",
        "  Data centre facilities              Your data (encryption, backups)",
        "  Network hardware                    IAM (who has access to what)",
        "  Hypervisor/virtualisation layer     OS patching (for IaaS/EC2)",
        "  Service availability (SLA)          Security group rules",
        "                                      Data classification",
        "",
        "Simple rule:",
        "  Cloud provider secures the CLOUD (infrastructure)",
        "  You secure what is IN the cloud (your code, data, access)",
        "```",
        "",
        "---",
        "",
        "## Mind Map",
        "",
        "```",
        "CLOUD FUNDAMENTALS",
        "|",
        "+-- WHY CLOUD",
        "|   +-- Pay per use (no upfront hardware)",
        "|   +-- Scale in minutes (not weeks)",
        "|   +-- Global reach (regions/AZs)",
        "|   +-- No hardware maintenance",
        "|",
        "+-- SERVICE MODELS",
        "|   +-- IaaS   (EC2: you manage OS, they manage hardware)",
        "|   +-- PaaS   (Elastic Beanstalk: you deploy app, they manage platform)",
        "|   +-- SaaS   (Gmail: use the software, manage nothing)",
        "|   +-- FaaS   (Lambda: pay per function execution)",
        "|",
        "+-- GEOGRAPHIC CONCEPTS",
        "|   +-- Region   (geographic area: us-east-1)",
        "|   +-- AZ       (data centre: us-east-1a)",
        "|   +-- Multi-AZ (high availability — survive one AZ failure)",
        "|",
        "+-- NETWORKING",
        "|   +-- VPC       (your private network)",
        "|   +-- Public subnet  (internet-facing: load balancers)",
        "|   +-- Private subnet (internal: databases, app servers)",
        "|   +-- Security Groups (stateful firewall)",
        "|",
        "+-- IDENTITY (IAM)",
        "|   +-- User, Group, Role, Policy",
        "|   +-- Least privilege principle",
        "|   +-- Use roles on EC2/Lambda, never access keys",
        "|",
        "+-- PRICING",
        "    +-- On-demand (per second, no commitment)",
        "    +-- Reserved  (1-3 year commitment, 72% discount)",
        "    +-- Spot      (cheapest, can be interrupted)",
        "    +-- Savings Plans (flexible commitment)",
        "```",
        "",
        "---",
        "",
        "## How Cloud Fundamentals Connects to Other Topics",
        "",
        "- **Docker + Kubernetes**: ECS runs Docker containers; EKS is managed Kubernetes.",
        "  K8s worker nodes are EC2 instances in a VPC.",
        "- **CI/CD**: Pipelines deploy to AWS using IAM roles with least-privilege access.",
        "  CodePipeline is AWS-native CI/CD.",
        "- **Databases**: RDS is managed PostgreSQL/MySQL in your VPC. DynamoDB is serverless NoSQL.",
        "- **Networking**: CloudFront CDN sits in front of your app. Route 53 handles DNS.",
        "  ALB is the load balancer distributing traffic across AZs.",
        "",
        "---",
        "",
        "## Common Beginner Mistakes",
        "",
        "1. **Hardcoding AWS access keys in code** — commit to git = key stolen in minutes by bots.",
        "   Use IAM roles on EC2/Lambda instead.",
        "2. **Everything in one AZ** — one power outage takes down your whole app.",
        "   Deploy across at least 2 AZs.",
        "3. **Overly permissive security groups** — ALLOW all traffic from 0.0.0.0/0 on all ports.",
        "   Only open the exact ports needed, from the exact sources needed.",
        "4. **No cost alerts** — cloud bills can spiral. Set a billing alert at your expected spend.",
        "5. **Public databases** — RDS should be in a private subnet. Never expose your database to the internet.",
        "6. **Ignoring the free tier** — for learning, stay within free tier. Set a $5 budget alert.",
        "7. **Using root account for daily work** — create IAM users with appropriate permissions.",
        "   Root account is for account-level emergencies only.",
        "",
        "---",
        "",
        "## References and Further Learning",
        "",
        "### Videos (Watch These!)",
        "- **AWS Certified Cloud Practitioner - Full Course** by freeCodeCamp:",
        "  https://www.youtube.com/watch?v=SOTamWNgDKc",
        "  - 13 hours. Complete beginner-to-practitioner. Even if you don't want the cert, chapters 1-4 are gold.",
        "- **Cloud Computing in 6 Minutes** by Simplilearn:",
        "  https://www.youtube.com/watch?v=M988_fsOSWo",
        "  - Quick overview of IaaS/PaaS/SaaS with examples.",
        "",
        "### Free Books and Articles",
        "- **AWS Well-Architected Framework**: https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html",
        "  - AWS best practices across 6 pillars: reliability, security, performance, cost, etc.",
        "- **AWS Free Tier guide**: https://aws.amazon.com/free/",
        "  - What you can use for free to practice. Start here.",
        "",
        "### Diagrams and Cheatsheets",
        "- **AWS Global Infrastructure map**: https://infrastructure.aws/",
        "  - Live map of all regions and AZs worldwide.",
        "- **AWS Shared Responsibility diagram**: search 'AWS shared responsibility model diagram'",
        "",
        "### Practice",
        "- **AWS Skill Builder** (free official training): https://skillbuilder.aws/",
        "  - 'AWS Cloud Practitioner Essentials' is a free 6-hour course.",
        "- **CloudQuest by AWS** (gamified cloud learning): https://aws.amazon.com/training/digital/aws-cloud-quest/",
    ])

    CLOUD_NEW_Q = [
        {"id":"cloud-q4","type":"mcq","prompt":"What is the main benefit of cloud computing over buying physical servers?",
         "choices":["Cloud servers are faster","You only pay for what you use and can scale in minutes without upfront hardware investment",
                    "Cloud is always cheaper","Cloud servers never fail"],
         "answerIndex":1,"explanation":"Cloud trades capital expenditure (buy hardware upfront) for operational expenditure (pay per use). You scale in minutes, not weeks, and pay nothing when idle.","tags":["cloud-basics","economics"]},
        {"id":"cloud-q5","type":"mcq","prompt":"An EC2 instance is an example of which service model?",
         "choices":["SaaS","PaaS","IaaS","FaaS"],
         "answerIndex":2,"explanation":"EC2 is Infrastructure as a Service. AWS provides the hardware and virtualisation, but you manage the OS, patching, runtime, and application. You have full control but more responsibility.","tags":["iaas","service-models"]},
        {"id":"cloud-q6","type":"mcq","prompt":"AWS Lambda is an example of which service model?",
         "choices":["IaaS","PaaS","SaaS","FaaS (serverless)"],
         "answerIndex":3,"explanation":"Lambda is Function as a Service. You write a function, AWS handles everything else: servers, OS, scaling, availability. You pay only per execution (milliseconds of compute time).","tags":["faas","serverless"]},
        {"id":"cloud-q7","type":"mcq","prompt":"What is the purpose of multiple Availability Zones (AZs) in one region?",
         "choices":["Reduce network latency","Provide lower costs","High availability — if one AZ has an outage (power, fire, hardware), the app keeps running in other AZs",
                    "Separate dev and prod environments"],
         "answerIndex":2,"explanation":"AZs are physically separate data centres with independent power/cooling/network. Deploying across multiple AZs means one AZ failure (which happens) does not take down your application.","tags":["availability-zones","high-availability"]},
        {"id":"cloud-q8","type":"mcq","prompt":"What is an IAM Role in AWS?",
         "choices":["A user account for humans","A set of allowed IP addresses","A temporary identity with permissions that services (EC2, Lambda) can assume — no hardcoded credentials needed",
                    "A VPC routing rule"],
         "answerIndex":2,"explanation":"IAM Roles are assumed by services (not humans). An EC2 instance assumes a role to get temporary credentials automatically rotated by AWS. This avoids hardcoding access keys — the most common AWS security mistake.","tags":["iam","security"]},
        {"id":"cloud-q9","type":"mcq","prompt":"An EC2 instance needs to read files from S3. What is the CORRECT way to provide credentials?",
         "choices":["Hardcode access key and secret in the application code","Create an IAM Role with S3 read permissions, attach it to the EC2 instance",
                    "SSH into the instance and run aws configure","Store credentials in /etc/environment"],
         "answerIndex":1,"explanation":"IAM Roles on EC2 provide temporary, automatically-rotated credentials via the instance metadata service. No hardcoding needed. Hardcoded keys in code are a critical security vulnerability.","tags":["iam","ec2","security"]},
        {"id":"cloud-q10","type":"mcq","prompt":"What is the difference between a public subnet and a private subnet in a VPC?",
         "choices":["Public subnets are cheaper","Public subnets have internet gateway routes (internet accessible); private subnets have no direct internet route (protected, used for databases and app servers)",
                    "Private subnets are faster","There is no difference"],
         "answerIndex":1,"explanation":"Public subnets have an Internet Gateway route — instances can have public IPs. Private subnets have no internet gateway — instances are not directly reachable from internet. Databases should always be in private subnets.","tags":["vpc","networking"]},
        {"id":"cloud-q11","type":"mcq","prompt":"What is the Principle of Least Privilege in cloud IAM?",
         "choices":["Give all users admin access for convenience","Give every identity only the minimum permissions it needs — nothing more. Reduces blast radius if credentials are compromised.",
                    "Use root account for all operations","Rotate passwords every 90 days"],
         "answerIndex":1,"explanation":"Least privilege limits damage. A compromised EC2 with only S3 read access cannot delete databases or spin up new instances. A compromised admin account can destroy everything.","tags":["iam","security","least-privilege"]},
        {"id":"cloud-q12","type":"mcq","prompt":"What AWS pricing model gives up to 90% discount but can be interrupted with 2 minutes notice?",
         "choices":["Reserved Instances","On-Demand","Spot Instances","Savings Plans"],
         "answerIndex":2,"explanation":"Spot Instances use spare AWS capacity at massive discounts. AWS can reclaim them with 2-minute notice when capacity is needed. Perfect for batch ML training, data processing — anything fault-tolerant.","tags":["pricing","spot-instances"]},
        {"id":"cloud-q13","type":"mcq","prompt":"What does S3 store?",
         "choices":["Virtual machines","Relational database records","Objects (files, images, videos, backups, static website assets) — any file up to 5TB",
                    "Docker container images only"],
         "answerIndex":2,"explanation":"S3 (Simple Storage Service) is object storage. Store any file — images, videos, backups, ML datasets, static websites. Infinitely scalable, 11 nines durability. Not a filesystem (no hierarchical directories).","tags":["s3","storage"]},
        {"id":"cloud-q14","type":"mcq","prompt":"What is the cloud provider's responsibility under the Shared Responsibility Model?",
         "choices":["Your application code security","Your IAM configuration","Security OF the cloud: physical data centres, hardware, virtualisation infrastructure, and service availability",
                    "Your data encryption"],
         "answerIndex":2,"explanation":"AWS secures the underlying infrastructure. You are responsible for what runs ON it: your code, your data, your IAM policies, your security groups, OS patching (for EC2). 'Security of the cloud vs security in the cloud.'","tags":["shared-responsibility","security"]},
        {"id":"cloud-q15","type":"mcq","prompt":"What is CloudFront used for?",
         "choices":["Running containers","Managed Kubernetes","A CDN (Content Delivery Network) that caches content at edge locations globally — serving users from nearby servers instead of your origin, reducing latency",
                    "VPC routing"],
         "answerIndex":2,"explanation":"CloudFront has 400+ edge locations worldwide. A user in Tokyo requesting your US-hosted image gets it from a nearby edge cache — milliseconds instead of hundreds of milliseconds. Also protects against DDoS (integrates with WAF).","tags":["cloudfront","cdn"]},
        {"id":"cloud-q16","type":"mcq","prompt":"What is the key difference between RDS and DynamoDB?",
         "choices":["RDS is serverless; DynamoDB is not","RDS = managed relational database (SQL, tables, joins, ACID); DynamoDB = serverless NoSQL key-value/document store (millisecond latency, infinite scale)",
                    "They are the same service","RDS is cheaper"],
         "answerIndex":1,"explanation":"RDS runs MySQL/PostgreSQL/etc. — structured data, SQL queries, joins, transactions. DynamoDB is NoSQL — flexible schema, built for high-throughput, low-latency reads/writes. Choose based on data model.","tags":["rds","dynamodb","databases"]},
        {"id":"cloud-q17","type":"mcq","prompt":"What is Infrastructure as Code (IaC)?",
         "choices":["Writing application code","Running code in the cloud","Defining cloud infrastructure in code files (YAML/JSON/TypeScript) that are version-controlled and applied automatically — AWS CloudFormation, CDK, Terraform",
                    "Serverless functions"],
         "answerIndex":2,"explanation":"IaC treats infrastructure like application code. Version controlled in git. Reproducible environments. Review infrastructure changes in PRs. CloudFormation (AWS), Terraform (multi-cloud), CDK (CloudFormation via real code).","tags":["iac","cloudformation"]},
        {"id":"cloud-q18","type":"multi","prompt":"Which of these belong in a PRIVATE subnet? (Select all that apply)",
         "choices":["RDS database","EC2 application server (no public access needed)","Load balancer (receives external traffic)","Redis ElastiCache"],
         "answerIndexes":[0,1,3],"explanation":"Databases (RDS), internal app servers, and caches should be in private subnets — no direct internet access. Load balancers need to be in public subnets to receive external traffic (they have a public IP).","tags":["vpc","subnets","security"]},
        {"id":"cloud-q19","type":"mcq","prompt":"What is a Security Group in AWS?",
         "choices":["An IAM group for security engineers","A stateful virtual firewall for EC2 instances — controls inbound and outbound traffic by IP, port, and protocol",
                    "An encryption service","A VPC routing table"],
         "answerIndex":1,"explanation":"Security Groups are stateful (if inbound is allowed, response is automatically allowed). They attach to EC2 instances and RDS. Default: deny all inbound, allow all outbound. Open only specific ports from specific sources.","tags":["security-groups","networking","security"]},
        {"id":"cloud-q20","type":"mcq","prompt":"What is the key advantage of a Reserved Instance over On-Demand pricing?",
         "choices":["Reserved Instances can be stopped easily","Reserved Instances are always available","Up to 72% cost reduction in exchange for a 1 or 3-year commitment — ideal for steady predictable workloads like production databases",
                    "Reserved Instances have no storage limit"],
         "answerIndex":2,"explanation":"On-demand flexibility costs more per hour. If you know a workload will run 24/7 for a year (production database, core API), Reserved Instances give huge savings. 1-year = ~40% off; 3-year = ~72% off.","tags":["pricing","reserved-instances"]},
    ]

    CLOUD_NEW_FC = [
        {"id":"cloud-fc4","front":"EC2 vs Lambda vs Fargate","back":"EC2 = IaaS (you manage OS, runtime). Lambda = FaaS pay per ms, no servers. Fargate = serverless containers (no EC2 to manage). Fargate = between EC2 and Lambda for container workloads.","tags":["compute","service-models"]},
        {"id":"cloud-fc5","front":"Public vs Private subnet rule","back":"Public subnet: has IGW route, instances get public IPs. Load balancers live here. Private subnet: no internet route. Databases, app servers, caches live here. Only reachable from within VPC.","tags":["vpc","networking"]},
        {"id":"cloud-fc6","front":"IAM Role vs IAM User","back":"User = person (human) with long-term credentials (password, access key). Role = identity for services/automation (temporary, auto-rotated credentials). Use roles for EC2/Lambda. NEVER use access keys on servers.","tags":["iam","security"]},
        {"id":"cloud-fc7","front":"On-Demand vs Reserved vs Spot","back":"On-Demand: pay per second, no commitment, most flexible, most expensive. Reserved: 1-3yr commit, 40-72% cheaper, use for steady workloads. Spot: 70-90% cheaper, can be interrupted, use for batch jobs.","tags":["pricing"]},
        {"id":"cloud-fc8","front":"S3 vs EBS vs EFS","back":"S3 = object storage (any file, accessed via HTTP API, globally unique URL). EBS = block storage (like an HD, attached to ONE EC2). EFS = shared filesystem (mounted by MULTIPLE EC2s simultaneously).","tags":["storage"]},
    ]

    d_cloud['guide'] = CLOUD_GUIDE
    qids = {q['id'] for q in d_cloud['questions']}
    for q in CLOUD_NEW_Q:
        if q['id'] not in qids:
            d_cloud['questions'].append(q)
    fcids = {f['id'] for f in d_cloud['flashcards']}
    for fc in CLOUD_NEW_FC:
        if fc['id'] not in fcids:
            d_cloud['flashcards'].append(fc)
    with open(p_cloud, 'w') as f:
        json.dump(d_cloud, f, indent=2, ensure_ascii=False)
    print(f"cloud-fundamentals.json done: guide={len(CLOUD_GUIDE)} q={len(d_cloud['questions'])} fc={len(d_cloud['flashcards'])}")

    # ── patch_aws_prac.py ──────────────────────────────────────────────────────────────────
    p = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/aws-practitioner.json')
    d = json.loads(p.read_text())

    GUIDE = "\n".join([
        "# AWS Practitioner Fundamentals",
        "",
        "## AWS in Plain English — Why It Exists",
        "",
        "AWS (Amazon Web Services) started because Amazon built a huge internal infrastructure",
        "to run amazon.com, then realised other companies needed the same thing.",
        "In 2006 they opened it up — rent Amazon's servers and infrastructure on-demand.",
        "Today AWS is the world's largest cloud provider, used by Netflix, Airbnb, NASA, startups,",
        "and Fortune 500 companies alike.",
        "",
        "**The core promise:** You get access to world-class infrastructure — data centres,",
        "networking, databases, security — without buying or managing any hardware.",
        "Pay only for what you use. Scale in minutes. Global in hours.",
        "",
        "```",
        "AWS has 200+ services across every category:",
        "  Compute:    EC2, Lambda, ECS, EKS, Fargate",
        "  Storage:    S3, EBS, EFS, Glacier",
        "  Database:   RDS, DynamoDB, ElastiCache, Redshift",
        "  Networking: VPC, CloudFront, Route 53, API Gateway",
        "  Security:   IAM, KMS, WAF, Shield, GuardDuty",
        "  AI/ML:      SageMaker, Bedrock, Rekognition, Transcribe",
        "  DevOps:     CodePipeline, CodeBuild, CloudFormation, CDK",
        "  Monitoring: CloudWatch, X-Ray, CloudTrail",
        "```",
        "",
        "---",
        "",
        "## Core Compute: EC2",
        "",
        "EC2 (Elastic Compute Cloud) is a virtual machine (VM) in the cloud.",
        "It is the most fundamental AWS service — everything else often runs on top of EC2.",
        "",
        "```",
        "EC2 instance = a Linux (or Windows) server you rent by the hour",
        "",
        "Instance types: different CPU/RAM/storage combinations",
        "  t3.micro:   2 vCPU,  1GB RAM   ($0.01/hr) - free tier, dev/test",
        "  t3.medium:  2 vCPU,  4GB RAM   ($0.04/hr) - small apps",
        "  m5.xlarge:  4 vCPU, 16GB RAM   ($0.19/hr) - general workloads",
        "  c5.2xlarge: 8 vCPU, 16GB RAM   ($0.34/hr) - CPU-intensive",
        "  r5.4xlarge:16 vCPU,128GB RAM   ($1.00/hr) - memory-intensive (Redis,DBs)",
        "  p3.2xlarge: 8 vCPU, 61GB RAM + V100 GPU  - ML training",
        "",
        "Instance type naming convention:",
        "  [family][generation].[size]",
        "  m5.xlarge",
        "  |  | ---",
        "  |  +-- generation (5th gen is newer/better than 4th gen)",
        "  +----- family: m=general, c=compute, r=memory, p=GPU",
        "```",
        "",
        "**Launching an EC2 instance (mental model):**",
        "```",
        "1. Choose AMI (Amazon Machine Image) = the OS template",
        "   Amazon Linux 2023, Ubuntu 22.04, Windows Server 2022",
        "",
        "2. Choose instance type (CPU/RAM)",
        "",
        "3. Configure networking",
        "   Which VPC? Which subnet (public/private)?",
        "",
        "4. Configure storage (EBS volume)",
        "   Root volume: OS disk (default 8GB, encrypted)",
        "",
        "5. Configure security group (firewall rules)",
        "   Allow port 22 (SSH) from your IP",
        "   Allow port 443 (HTTPS) from anywhere",
        "",
        "6. Choose or create key pair (for SSH access)",
        "",
        "7. Launch -> running in ~60 seconds",
        "",
        "8. SSH: ssh -i mykey.pem ec2-user@<public-ip>",
        "```",
        "",
        "---",
        "",
        "## S3 — Simple Storage Service",
        "",
        "S3 is AWS's object storage. Think of it as an infinitely large, durable,",
        "globally accessible hard drive for files.",
        "",
        "```",
        "Key concepts:",
        "",
        "BUCKET:",
        "  Container for objects (files)",
        "  Globally unique name across all AWS accounts",
        "  Belongs to one region",
        "  Example: my-company-logs-2026",
        "",
        "OBJECT:",
        "  A file stored in a bucket",
        "  Key = the 'path': photos/2026/01/vacation.jpg",
        "  Value = the file data (any format, up to 5TB)",
        "  Metadata: content-type, custom tags",
        "",
        "URL: https://my-bucket.s3.amazonaws.com/photos/vacation.jpg",
        "",
        "STORAGE CLASSES (cost vs retrieval speed):",
        "  S3 Standard:            Frequent access, millisecond retrieval",
        "  S3-IA (Infrequent):     Lower cost, retrieval fee, 30-day min",
        "  S3 Glacier Instant:     Archive, millisecond retrieval",
        "  S3 Glacier Flexible:    Archive, 1-5 hour retrieval, cheapest storage",
        "",
        "COMMON USE CASES:",
        "  Static website hosting (React/Vue SPA)",
        "  Application logs and backups",
        "  Large file storage (videos, datasets)",
        "  Data lake for analytics",
        "  Docker image layer caching",
        "  CloudFront origin (serve files globally)",
        "```",
        "",
        "**S3 access control:**",
        "```",
        "Bucket Policy (JSON):  who can access which objects",
        "IAM Policy:            which IAM identities can access which bucket",
        "ACLs:                  legacy, avoid for new buckets",
        "Pre-signed URLs:       temporary URLs giving time-limited access to private objects",
        "",
        "Block Public Access:   account-level setting, blocks all public access",
        "  Enable this on all buckets unless the bucket hosts a public website.",
        "  A misconfigured S3 public bucket has leaked millions of records.",
        "```",
        "",
        "---",
        "",
        "## VPC — Virtual Private Cloud",
        "",
        "VPC is your private network in AWS. All your resources (EC2, RDS, Lambda) live inside a VPC.",
        "",
        "```",
        "VPC: 10.0.0.0/16  (65,536 IP addresses)",
        "|",
        "+-- Public Subnet: 10.0.1.0/24",
        "|   +-- Internet Gateway (allows inbound + outbound internet)",
        "|   +-- Load Balancer (public IP, receives external traffic)",
        "|   +-- Bastion Host (SSH jump server)",
        "|",
        "+-- Private Subnet: 10.0.2.0/24",
        "|   +-- EC2 App Servers (no public IP)",
        "|   +-- RDS Database (no public IP)",
        "|   +-- ElastiCache (no public IP)",
        "|",
        "+-- NAT Gateway (in public subnet)",
        "    Allows private subnet resources to reach internet (outbound only)",
        "    e.g. EC2 app server downloads packages from internet",
        "    but internet cannot initiate connections TO private EC2",
        "",
        "Security Groups:  stateful firewall attached to instances",
        "  ALLOW port 443 from 0.0.0.0/0   (anyone can reach HTTPS)",
        "  ALLOW port 5432 from sg-app      (only app security group can reach DB)",
        "",
        "Route Tables:  rules for how traffic is routed",
        "  Public subnet route: 0.0.0.0/0 -> Internet Gateway",
        "  Private subnet route: 0.0.0.0/0 -> NAT Gateway",
        "```",
        "",
        "---",
        "",
        "## IAM — Identity and Access Management",
        "",
        "IAM controls who can do what in your AWS account. Get this wrong and",
        "your entire AWS account can be compromised.",
        "",
        "```",
        "USERS:    Human identities (Alice, Bob)",
        "          Credentials: password (console) or access keys (CLI/API)",
        "          Best practice: human users should use SSO, not long-term access keys",
        "",
        "GROUPS:   Collections of users sharing permissions",
        "          'developers' group: read S3, describe EC2, invoke Lambda",
        "          'admins' group: full access",
        "",
        "ROLES:    Identities for services (not humans)",
        "          EC2 instance assumes role -> gets temporary credentials",
        "          Lambda assumes role -> can write to DynamoDB",
        "          No hardcoded secrets! Credentials auto-rotate every hour",
        "",
        "POLICIES: JSON permission documents attached to users/groups/roles",
        "  {",
        "    'Effect': 'Allow',",
        "    'Action': 's3:GetObject',",
        "    'Resource': 'arn:aws:s3:::my-bucket/*'",
        "  }",
        "",
        "CRITICAL RULE: Never use root account for daily work.",
        "  Root = god mode. Create an admin IAM user for yourself.",
        "  Enable MFA on root account immediately.",
        "  Root account credentials = keys to the kingdom.",
        "```",
        "",
        "---",
        "",
        "## RDS — Relational Database Service",
        "",
        "RDS is managed relational database. AWS handles: installation, patching,",
        "backups, replication, failover. You manage: schema, queries, data.",
        "",
        "```",
        "Supported engines:",
        "  PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, Aurora",
        "",
        "Aurora:",
        "  AWS's own MySQL/PostgreSQL-compatible engine",
        "  5x faster than MySQL, 3x faster than PostgreSQL",
        "  Storage auto-scales up to 128TB",
        "  Multi-AZ by default, automated failover",
        "  Aurora Serverless: scales compute to zero when idle",
        "",
        "Key RDS features:",
        "  Multi-AZ:           automatic standby in another AZ, failover in 60-120s",
        "  Read Replicas:      read-only copies for offloading read traffic",
        "  Automated backups:  daily snapshot + transaction logs (point-in-time recovery)",
        "  Encryption at rest: KMS-managed keys",
        "",
        "RDS in your VPC (always):",
        "  RDS in private subnet = not reachable from internet",
        "  Only your app servers (same VPC) can reach it",
        "  Security group: ALLOW port 5432 from app-server security group only",
        "```",
        "",
        "---",
        "",
        "## DynamoDB — NoSQL at Scale",
        "",
        "DynamoDB is AWS's serverless NoSQL database. Zero servers to manage.",
        "Single-digit millisecond latency at any scale.",
        "",
        "```",
        "Core concepts:",
        "  TABLE:          collection of items (like a table in SQL, but schemaless)",
        "  ITEM:           a record (like a row), JSON-like, up to 400KB",
        "  PRIMARY KEY:    uniquely identifies each item",
        "    Partition key:         single attribute (userId)",
        "    Partition + Sort key:  two attributes (userId + timestamp)",
        "",
        "Capacity modes:",
        "  ON-DEMAND:    pay per read/write request, scales automatically, good for unpredictable",
        "  PROVISIONED:  specify RCU/WCU, predictable traffic, cheaper at steady load",
        "",
        "Global Secondary Index (GSI):",
        "  Query on non-primary-key attributes",
        "  Table has userId as PK, but you want to query by email -> add GSI on email",
        "",
        "DynamoDB Streams:",
        "  Record every change (insert/update/delete) as a stream",
        "  Trigger Lambda on change -> event-driven architecture",
        "",
        "When to use DynamoDB vs RDS:",
        "  DynamoDB:  simple access patterns, high throughput, unlimited scale, serverless",
        "  RDS:       complex queries, JOINs, transactions, relational data model",
        "```",
        "",
        "---",
        "",
        "## CloudWatch — Monitoring and Observability",
        "",
        "```",
        "CloudWatch is AWS's monitoring service. Collect, visualise, alert on:",
        "  - Metrics: CPU, memory, request count, error rate, latency",
        "  - Logs: application logs, Lambda logs, VPC flow logs",
        "  - Alarms: trigger actions when metric crosses threshold",
        "  - Dashboards: visualise metrics in real-time",
        "",
        "Key metrics to monitor:",
        "  EC2:    CPUUtilization, NetworkIn/Out, DiskReadOps",
        "  RDS:    DatabaseConnections, FreeStorageSpace, CPUUtilization, ReadLatency",
        "  Lambda: Duration, Errors, Throttles, ConcurrentExecutions",
        "  SQS:    ApproximateNumberOfMessagesVisible, AgeOfOldestMessage",
        "  ALB:    RequestCount, TargetResponseTime, HTTPCode_ELB_5XX",
        "",
        "CloudWatch Alarms:",
        "  Metric: Lambda Errors > 10 per 5 min",
        "  Action: Send SNS notification -> trigger PagerDuty -> wake up engineer",
        "",
        "CloudWatch Logs Insights (query language):",
        "  fields @timestamp, @message",
        "  | filter @message like /ERROR/",
        "  | stats count() by bin(5m)",
        "  | sort @timestamp desc",
        "  | limit 100",
        "",
        "CloudTrail (different from CloudWatch!):",
        "  Logs ALL AWS API calls: who did what, when, from where",
        "  'Who deleted that S3 bucket at 3am?' -> CloudTrail shows you",
        "  Enable in all accounts and regions. Required for compliance.",
        "```",
        "",
        "---",
        "",
        "## Elastic Load Balancing (ELB)",
        "",
        "```",
        "Load balancer distributes incoming traffic across multiple EC2/containers.",
        "",
        "ALB (Application Load Balancer) - Layer 7 (HTTP):",
        "  Routes by URL path, hostname, headers",
        "  /api/* -> target group 1 (API servers)",
        "  /static/* -> target group 2 (static file servers)",
        "  Header: X-Version: v2 -> new version canary group",
        "  Supports WebSockets, HTTP/2, gRPC",
        "",
        "NLB (Network Load Balancer) - Layer 4 (TCP):",
        "  Ultra-low latency (millions of requests per second)",
        "  Routes by IP/port, no HTTP awareness",
        "  Use for: gaming, financial trading, IoT",
        "",
        "Health checks:",
        "  ALB sends requests to /health endpoint on each target",
        "  Unhealthy target -> removed from rotation until healthy",
        "  New EC2 instance -> waits for N consecutive health checks -> added to rotation",
        "",
        "Auto Scaling Group:",
        "  Automatically add/remove EC2 instances based on load",
        "  Scale out when CPU > 70%, scale in when CPU < 30%",
        "  ALB automatically routes to new instances as they join",
        "```",
        "",
        "---",
        "",
        "## Well-Architected Framework — Five Pillars",
        "",
        "```",
        "AWS Well-Architected Framework = best practices guide for cloud architecture.",
        "Five pillars:",
        "",
        "1. OPERATIONAL EXCELLENCE:",
        "   Run and monitor systems, improve processes continuously.",
        "   IaC for everything, small reversible changes, automate operations.",
        "",
        "2. SECURITY:",
        "   Protect data and systems. Least privilege IAM, encrypt at rest and in transit,",
        "   enable CloudTrail, patch regularly, use private subnets.",
        "",
        "3. RELIABILITY:",
        "   Recover from failures, meet demand.",
        "   Multi-AZ deployments, auto-scaling, backups, chaos engineering.",
        "",
        "4. PERFORMANCE EFFICIENCY:",
        "   Use resources efficiently. Right-size instances, use managed services,",
        "   CloudFront for global distribution, caching.",
        "",
        "5. COST OPTIMISATION:",
        "   Avoid waste. Right-size, use Reserved Instances for steady workloads,",
        "   Spot for batch, turn off dev environments at night, use S3 lifecycle policies.",
        "```",
        "",
        "---",
        "",
        "## Mind Map",
        "",
        "```",
        "AWS PRACTITIONER",
        "|",
        "+-- COMPUTE",
        "|   +-- EC2 (VMs, hourly billing, AMI, instance types)",
        "|   +-- Lambda (serverless functions)",
        "|   +-- ECS/EKS (containers)",
        "|",
        "+-- STORAGE",
        "|   +-- S3 (object storage, static websites, backups)",
        "|   +-- EBS (block storage for EC2)",
        "|   +-- EFS (shared filesystem)",
        "|",
        "+-- DATABASE",
        "|   +-- RDS (managed relational: PostgreSQL/MySQL/Aurora)",
        "|   +-- DynamoDB (NoSQL, serverless, ms latency)",
        "|   +-- ElastiCache (managed Redis/Memcached)",
        "|",
        "+-- NETWORKING",
        "|   +-- VPC (private network, subnets, routing)",
        "|   +-- ALB/NLB (load balancers)",
        "|   +-- CloudFront (CDN)",
        "|   +-- Route 53 (DNS)",
        "|",
        "+-- SECURITY",
        "|   +-- IAM (users, roles, policies, least privilege)",
        "|   +-- KMS (key management)",
        "|   +-- CloudTrail (API audit log)",
        "|",
        "+-- MONITORING",
        "    +-- CloudWatch (metrics, logs, alarms)",
        "    +-- X-Ray (distributed tracing)",
        "```",
        "",
        "---",
        "",
        "## References and Further Learning",
        "",
        "### Videos (Watch These!)",
        "- **AWS Certified Cloud Practitioner - Full Course** by freeCodeCamp:",
        "  https://www.youtube.com/watch?v=SOTamWNgDKc",
        "  - 13 hours. Complete beginner to practitioner. Chapters 1-5 are essential.",
        "- **AWS Services Explained** by Fireship:",
        "  https://www.youtube.com/watch?v=M988_fsOSWo",
        "  - Quick 6-minute overview. Great starting point.",
        "",
        "### Free Books and Articles",
        "- **AWS Well-Architected Framework**: https://aws.amazon.com/architecture/well-architected/",
        "- **AWS Architecture Center**: https://aws.amazon.com/architecture/",
        "  - Reference architectures for common patterns (3-tier web, serverless, etc.)",
        "",
        "### Practice",
        "- **AWS Skill Builder** (official free training): https://skillbuilder.aws/",
        "  - 'AWS Cloud Practitioner Essentials' = 6 hours, free.",
        "- **AWS Free Tier**: https://aws.amazon.com/free/",
        "  - 12 months free EC2, always-free Lambda/DynamoDB tier.",
    ])

    NEW_Q = [
        {"id":"aws-prac-q1","type":"mcq","prompt":"What is EC2?",
         "choices":["AWS email service","A serverless function","A virtual machine (server) you rent in the cloud — choose OS, CPU, RAM, and pay by the hour",
                    "AWS database service"],
         "answerIndex":2,"explanation":"EC2 (Elastic Compute Cloud) is the foundational AWS compute service. You get a virtual Linux/Windows machine, SSH in, install your app, and pay per second it runs. It is the most flexible but most ops-heavy compute option.","tags":["ec2","compute"]},
        {"id":"aws-prac-q2","type":"mcq","prompt":"What does S3 store?",
         "choices":["Virtual machines","Running code","Objects (any file up to 5TB) in globally unique named buckets — images, videos, backups, static websites, datasets",
                    "Container images only"],
         "answerIndex":2,"explanation":"S3 is object storage. Not a filesystem — each object has a key (like a path) and value (file data). 11 nines durability. Used for: static websites, application backups, data lakes, logs, ML datasets, CloudFront origins.","tags":["s3","storage"]},
        {"id":"aws-prac-q3","type":"mcq","prompt":"What is the core purpose of an IAM Role?",
         "choices":["An IAM role is for human users","An IAM role provides temporary, automatically-rotated credentials to AWS services (EC2, Lambda) — eliminates the need for hardcoded access keys",
                    "IAM Roles are for read-only access","IAM Roles are required for billing"],
         "answerIndex":1,"explanation":"Roles are assumed by services. EC2 instance assumes a role -> gets temporary credentials refreshed every hour. Lambda assumes a role -> can write to DynamoDB. No hardcoded secrets in config files. This is the correct pattern for service-to-service access.","tags":["iam","roles","security"]},
        {"id":"aws-prac-q4","type":"mcq","prompt":"What is the difference between RDS and DynamoDB?",
         "choices":["RDS is NoSQL, DynamoDB is relational","RDS = managed relational database (SQL, joins, ACID transactions). DynamoDB = managed NoSQL key-value/document store (ms latency, infinite scale, serverless)",
                    "They are the same service","DynamoDB only works with Lambda"],
         "answerIndex":1,"explanation":"RDS: SQL engine (PostgreSQL/MySQL), complex queries with joins, ACID transactions, vertical scaling. DynamoDB: NoSQL, simple key-based access, scales horizontally to any load, pay per request, single-digit ms latency.","tags":["rds","dynamodb","databases"]},
        {"id":"aws-prac-q5","type":"mcq","prompt":"Why should RDS always be in a private subnet?",
         "choices":["Private subnets are faster","To reduce costs","Databases in public subnets are directly accessible from the internet — a security risk. Private subnet = only VPC-internal resources can connect.",
                    "RDS requires private subnets"],
         "answerIndex":2,"explanation":"RDS in a public subnet has a public IP. Any attacker on the internet can attempt connections. Private subnet = no public IP, unreachable from internet. Only app servers in the same VPC (via security group rules) can connect.","tags":["rds","vpc","security"]},
        {"id":"aws-prac-q6","type":"mcq","prompt":"What does CloudTrail record?",
         "choices":["Application logs","AWS API calls — who did what action, when, from which IP, with what result across your entire AWS account",
                    "Network traffic","CloudWatch metrics"],
         "answerIndex":1,"explanation":"CloudTrail is the audit log for your AWS account. Every API call is logged: 'user alice deleted security group sg-123 at 14:32 from IP 1.2.3.4'. Essential for security auditing, compliance, and incident investigation.","tags":["cloudtrail","security","auditing"]},
        {"id":"aws-prac-q7","type":"mcq","prompt":"What is an Application Load Balancer (ALB) used for?",
         "choices":["Storing application data","Running Lambda functions","Distributing HTTP/HTTPS traffic across multiple EC2/container targets, with routing by URL path and hostname",
                    "Encrypting S3 data"],
         "answerIndex":2,"explanation":"ALB operates at Layer 7 (HTTP). Routes /api/* to API servers, /static/* to static file servers. Health-checks backend targets, removes unhealthy ones from rotation. Works with EC2, ECS containers, Lambda, and Kubernetes pods.","tags":["alb","load-balancing","networking"]},
        {"id":"aws-prac-q8","type":"mcq","prompt":"What is CloudFront?",
         "choices":["A compute service","AWS CDN (Content Delivery Network) — caches content at 400+ edge locations worldwide so users get content from a nearby server, reducing latency",
                    "A database service","A VPN service"],
         "answerIndex":1,"explanation":"CloudFront has edge locations globally. User in Tokyo requests your US-hosted image -> gets it from Tokyo edge cache (milliseconds) instead of US server (hundreds of ms). Also protects against DDoS and integrates with WAF.","tags":["cloudfront","cdn","networking"]},
        {"id":"aws-prac-q9","type":"mcq","prompt":"What is the Principle of Least Privilege in IAM?",
         "choices":["Grant all permissions and revoke as needed","Give every IAM identity only the exact minimum permissions it needs — nothing more. Limits blast radius if credentials are compromised.",
                    "Only root account should have policies","Never deny any action"],
         "answerIndex":1,"explanation":"An EC2 with only s3:GetObject on one bucket can only read that bucket — even if credentials are stolen. An EC2 with AdministratorAccess: attacker controls your entire AWS account. Start with zero, add permissions as needed.","tags":["iam","security","least-privilege"]},
        {"id":"aws-prac-q10","type":"mcq","prompt":"What is an AWS Security Group?",
         "choices":["An IAM group for security engineers","A stateful virtual firewall for EC2/RDS instances — controls which inbound/outbound traffic is allowed by IP address, port, and protocol",
                    "A VPC routing table","An encryption service"],
         "answerIndex":1,"explanation":"Security Groups are instance-level firewalls. Stateful: if inbound connection is allowed, the response is automatically allowed. Default: deny all inbound. Your job: ALLOW only the specific ports from specific sources your app needs.","tags":["security-groups","vpc","security"]},
        {"id":"aws-prac-q11","type":"mcq","prompt":"What is the S3 Block Public Access setting?",
         "choices":["Prevents S3 from being accessed from other regions","Account-level safeguard that overrides all bucket policies/ACLs to prevent any public access — prevents accidental data exposure",
                    "Encrypts all S3 data","Limits S3 storage size"],
         "answerIndex":1,"explanation":"Misconfigured S3 public buckets have caused massive data breaches. Block Public Access = account-level killswitch. Enable it everywhere and only disable for specific buckets that genuinely need public access (static website hosting).","tags":["s3","security","public-access"]},
        {"id":"aws-prac-q12","type":"mcq","prompt":"What is Auto Scaling in AWS?",
         "choices":["Automatically provisions new AWS accounts","Automatically adds or removes EC2 instances based on demand — scale out during traffic spikes, scale in when traffic drops",
                    "Automatically upgrades instance types","Automatic cost optimisation"],
         "answerIndex":1,"explanation":"Auto Scaling Group (ASG) maintains a fleet of EC2 instances. Define: min (always keep N), max (never exceed N), desired (target). Scaling policies: add instance when CPU > 70%, remove when CPU < 30%. Works with ALB to add new instances to rotation.","tags":["auto-scaling","ec2","elasticity"]},
        {"id":"aws-prac-q13","type":"mcq","prompt":"What is AWS CloudFormation?",
         "choices":["A monitoring service","Infrastructure as Code — define AWS resources in YAML/JSON templates, deploy and manage them consistently",
                    "A billing service","A container registry"],
         "answerIndex":1,"explanation":"CloudFormation lets you declare: 'I want a VPC with 2 subnets, an EC2 in the private subnet, an RDS, and a security group'. CF creates them in the right order, handles dependencies. Version-controlled infra, reproducible environments.","tags":["cloudformation","iac","devops"]},
        {"id":"aws-prac-q14","type":"mcq","prompt":"What is AWS KMS used for?",
         "choices":["Key-based routing in DynamoDB","Managed encryption key service — create, store, and control cryptographic keys used to encrypt S3, EBS, RDS, DynamoDB data",
                    "Kubernetes service","Load balancing"],
         "answerIndex":1,"explanation":"KMS (Key Management Service) manages encryption keys. You never see the raw key material — you just say 'encrypt this data with my key'. AWS handles key storage, rotation, and access control. All major AWS services integrate with KMS for encryption at rest.","tags":["kms","security","encryption"]},
        {"id":"aws-prac-q15","type":"mcq","prompt":"What is a NAT Gateway and why is it needed?",
         "choices":["Network Address Table — routes traffic between regions","Allows resources in PRIVATE subnets to make OUTBOUND internet connections (download packages, call APIs) without being reachable FROM the internet",
                    "A VPN endpoint","A firewall for public subnets"],
         "answerIndex":1,"explanation":"Private subnet EC2s need to download OS updates, call third-party APIs — but should not have public IPs. NAT Gateway (in public subnet) receives their outbound traffic, routes it to internet with NAT Gateway's public IP. Internet sees NAT Gateway IP, not EC2.","tags":["nat","vpc","networking"]},
        {"id":"aws-prac-q16","type":"mcq","prompt":"What is the difference between CloudWatch and CloudTrail?",
         "choices":["They are the same","CloudWatch = performance monitoring (metrics, logs, alarms). CloudTrail = security audit log (who made what AWS API call, when, from where). Both are essential.",
                    "CloudTrail is newer","CloudWatch is for security only"],
         "answerIndex":1,"explanation":"CloudWatch: your app's health (CPU, errors, latency). CloudTrail: your account's security audit (who changed IAM policy, who deleted the S3 bucket). Enable both. CloudTrail should log to a separate account so attackers cannot delete the evidence.","tags":["cloudwatch","cloudtrail","monitoring"]},
        {"id":"aws-prac-q17","type":"mcq","prompt":"What is Route 53?",
         "choices":["EC2 instance type","AWS's managed DNS service — translates domain names (myapp.com) to IP addresses. Also supports health checks and failover routing.",
                    "A load balancer","A CDN service"],
         "answerIndex":1,"explanation":"Route 53 is AWS DNS. Register domains, create records (A, CNAME, ALIAS), configure routing policies: simple, weighted (A/B testing), latency-based (route to nearest region), failover (primary/standby). Integrates with CloudFront, ALB, S3.","tags":["route53","dns","networking"]},
        {"id":"aws-prac-q18","type":"mcq","prompt":"What is ElastiCache?",
         "choices":["A custom cache service you deploy on EC2","Managed Redis or Memcached — in-memory cache that sits in front of your database to serve frequent queries in microseconds instead of hitting the DB",
                    "AWS caching for Lambda only","CDN cache"],
         "answerIndex":1,"explanation":"ElastiCache Redis: sub-millisecond reads, data structures (sorted sets, pub/sub), persistence, atomic operations. ElastiCache Memcached: simpler, multi-threaded, pure cache. Use in front of RDS to handle read-heavy traffic without scaling the DB.","tags":["elasticache","redis","caching"]},
        {"id":"aws-prac-q19","type":"multi","prompt":"Which AWS services are ALWAYS in a private subnet in a well-architected 3-tier web app? (Select all that apply)",
         "choices":["Application Load Balancer","EC2 application servers","RDS database","ElastiCache Redis"],
         "answerIndexes":[1,2,3],"explanation":"ALB must be in a public subnet to receive internet traffic. App servers, databases, and caches have no reason to be publicly accessible — private subnet protects them from direct internet exposure. Only ALB (and NAT GW) go in public subnets.","tags":["vpc","architecture","security"]},
        {"id":"aws-prac-q20","type":"mcq","prompt":"What is the AWS Free Tier?",
         "choices":["All AWS services are free","Selected services are free up to defined usage limits — t2.micro EC2 for 12 months, Lambda 1M requests forever, S3 5GB forever, DynamoDB 25GB forever",
                    "Free tier applies only to new services","Free tier requires a credit card with no charge"],
         "answerIndex":1,"explanation":"AWS Free Tier has three categories: 12-month free (EC2 t2.micro, S3 5GB), always free (Lambda 1M/mo, DynamoDB 25GB, CloudWatch 10 metrics), and trials. A credit card is required but you are not charged if you stay within limits.","tags":["free-tier","pricing"]},
    ]

    NEW_FC = [
        {"id":"aws-prac-fc1","front":"EC2 vs Lambda vs Fargate choice","back":"EC2: full control, steady traffic, long-running, manage OS. Lambda: event-driven, sporadic, <15min, zero ops, pay per call. Fargate: containers, no EC2 mgmt, longer tasks. Default starting point: Lambda for new APIs if fits constraints.","tags":["compute","ec2","lambda"]},
        {"id":"aws-prac-fc2","front":"S3 vs EBS vs EFS","back":"S3: object store (files), HTTP API access, infinite scale, cheap. EBS: block device attached to ONE EC2 (like a hard drive). EFS: shared POSIX filesystem mounted by MULTIPLE EC2s simultaneously. Each has distinct use cases.","tags":["storage","s3","ebs","efs"]},
        {"id":"aws-prac-fc3","front":"IAM: User vs Group vs Role vs Policy","back":"User=human identity. Group=users sharing permissions. Role=identity for services/apps (temporary creds, no passwords). Policy=JSON permission document attached to any of the above. Roles > hardcoded access keys always.","tags":["iam","security"]},
        {"id":"aws-prac-fc4","front":"RDS Multi-AZ vs Read Replica","back":"Multi-AZ: standby replica in another AZ for HIGH AVAILABILITY. Auto-failover in 60s. NOT for read scaling. Read Replica: async copy for READ SCALING. No automatic failover. You promote manually.","tags":["rds","high-availability"]},
        {"id":"aws-prac-fc5","front":"CloudWatch vs CloudTrail","back":"CloudWatch: operational monitoring (metrics, logs, alarms). 'Is my app healthy?' CloudTrail: security audit ('who changed what in my AWS account?'). Both are mandatory. CloudTrail logs to isolated account so attackers can't delete evidence.","tags":["cloudwatch","cloudtrail","monitoring"]},
        {"id":"aws-prac-fc6","front":"VPC public vs private subnet rule","back":"Public subnet: has internet gateway route, resources get public IPs. For: ALB, NAT Gateway, bastion hosts. Private subnet: no internet route, no public IPs. For: EC2 app servers, RDS, ElastiCache. Everything except the front door stays private.","tags":["vpc","networking","security"]},
        {"id":"aws-prac-fc7","front":"Well-Architected 5 pillars","back":"1.Operational Excellence (automate, IaC, small changes)  2.Security (least privilege, encrypt, trail)  3.Reliability (multi-AZ, backups, auto-recover)  4.Performance (right-size, CDN, cache)  5.Cost (reserved, spot, turn off idle)","tags":["well-architected"]},
        {"id":"aws-prac-fc8","front":"Top 3 AWS security mistakes","back":"1. Root account for daily work (create IAM user, enable MFA on root)  2. Hardcoded access keys in code (use IAM roles)  3. Public S3 bucket (enable Block Public Access everywhere). These three cause 90% of AWS security incidents.","tags":["security","iam","s3"]},
    ]

    d['guide'] = GUIDE
    d['questions'] = NEW_Q
    d['flashcards'] = NEW_FC

    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"aws-practitioner.json done: guide={len(GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ── patch_aws_mastery.py ──────────────────────────────────────────────────────────────────
    p = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/aws-mastery.json')
    d = json.loads(p.read_text())

    GUIDE = "\n".join([
        "# AWS Mastery — Lambda, API Gateway, CloudFormation, CDK",
        "",
        "## Beyond the Basics — What This Course Covers",
        "",
        "AWS Practitioner gives you the vocabulary. AWS Mastery is about building real systems.",
        "This topic focuses on the serverless-first, infrastructure-as-code approach that",
        "modern AWS engineers use daily.",
        "",
        "```",
        "The serverless stack you will master:",
        "",
        "  Client Browser/Mobile",
        "        |",
        "        | HTTPS",
        "        v",
        "  API Gateway   --- routes requests by path/method",
        "        |",
        "        v",
        "  Lambda Functions  --- stateless business logic",
        "        |",
        "        v",
        "  DynamoDB / RDS / S3 / ElastiCache  --- data tier",
        "",
        "All of this defined in code (CDK/SAM/CloudFormation)",
        "Deployed and updated via CI/CD pipeline",
        "```",
        "",
        "---",
        "",
        "## Lambda Deep Dive — Memory, Concurrency, Invocation Types",
        "",
        "```",
        "MEMORY AND CPU:",
        "  Lambda: 128MB - 10,240MB memory",
        "  CPU is proportional to memory (no separate CPU setting)",
        "  128MB  = 0.125 vCPU",
        "  1024MB = 1 vCPU",
        "  10GB   = ~6 vCPU",
        "",
        "  Key insight: increasing memory often reduces duration enough to be cost-neutral",
        "  or cheaper. Profile your function.",
        "",
        "  Cost = (duration in ms) x (memory in GB) x price_per_GB_second",
        "  512MB for 100ms vs 1024MB for 50ms = same cost, twice the speed",
        "",
        "INVOCATION TYPES:",
        "  Synchronous:  caller waits for response",
        "    API Gateway -> Lambda -> caller gets response",
        "    If Lambda errors: caller immediately gets error",
        "",
        "  Asynchronous: caller doesn't wait",
        "    S3 event, SNS, EventBridge -> Lambda",
        "    Lambda retries 2x on failure",
        "    Configure DLQ for failed events",
        "",
        "  Stream/Poll:  Lambda polls the source",
        "    SQS, Kinesis, DynamoDB Streams -> Lambda",
        "    Lambda manages polling, you manage batch size and concurrency",
        "",
        "CONCURRENCY TYPES:",
        "  Unreserved concurrency:  shares account limit (default 1000)",
        "  Reserved concurrency:    guarantees N for this function, caps it at N",
        "  Provisioned concurrency: pre-warms containers (eliminates cold start)",
        "",
        "LAMBDA EXECUTION CONTEXT REUSE:",
        "  INIT code (outside handler):  runs once per cold start",
        "    db_client = boto3.client('dynamodb')     # runs once",
        "    secret = get_secret()                     # runs once",
        "",
        "  HANDLER code:  runs on every invocation",
        "    def handler(event, context):",
        "        result = db_client.get_item(...)     # reuses connection",
        "        return result",
        "```",
        "",
        "---",
        "",
        "## API Gateway — Types and Configuration",
        "",
        "API Gateway is the front door for your Lambda-based APIs.",
        "Two main flavours:",
        "",
        "```",
        "REST API (API Gateway v1):",
        "  Full-featured: request/response transformation, API keys, usage plans,",
        "  WAF integration, per-stage deployments, stage variables",
        "  More expensive, more configuration",
        "  Use when: you need API keys for third-party access, custom authorisers,",
        "  request validation, response mapping",
        "",
        "HTTP API (API Gateway v2):",
        "  Simpler, 70% cheaper than REST API",
        "  Lower latency",
        "  Supports: JWT authorisers, CORS, Lambda proxy",
        "  Missing: API keys, usage plans, request/response transformation",
        "  Use when: simple Lambda proxy, internal microservices, JWT auth",
        "",
        "REQUEST FLOW:",
        "  Browser sends: POST /users",
        "        |",
        "        v",
        "  API Gateway receives request",
        "  Validates (optional: request schema, API key)",
        "  Applies authoriser (optional: Lambda authoriser, JWT)",
        "        |",
        "        v",
        "  Lambda invoked with event:",
        "  {",
        "    httpMethod: 'POST',",
        "    path: '/users',",
        "    headers: {...},",
        "    body: '{\"name\": \"Alice\"}'",
        "  }",
        "        |",
        "        v",
        "  Lambda returns:",
        "  {",
        "    statusCode: 201,",
        "    headers: {'Content-Type': 'application/json'},",
        "    body: '{\"userId\": \"abc123\"}'",
        "  }",
        "        |",
        "        v",
        "  API Gateway forwards response to browser",
        "",
        "AUTHORISATION:",
        "  Lambda Authoriser:  custom Bearer token validation lambda",
        "                      returns IAM policy allowing/denying access",
        "  JWT Authoriser:     API Gateway validates JWT against JWKS endpoint",
        "                      (Cognito, Auth0, custom)",
        "  IAM Authoriser:     AWS Signature V4 — for service-to-service calls",
        "  Cognito Authoriser: built-in Cognito User Pool integration",
        "```",
        "",
        "---",
        "",
        "## CloudFormation — Infrastructure as Code",
        "",
        "CloudFormation lets you define ALL your AWS infrastructure in a YAML/JSON template.",
        "The same template, deployed twice, creates identical environments every time.",
        "",
        "```yaml",
        "# cloudformation-template.yaml",
        "AWSTemplateFormatVersion: '2010-09-09'",
        "Description: Simple web app infrastructure",
        "",
        "Parameters:",
        "  Environment:",
        "    Type: String",
        "    AllowedValues: [dev, staging, production]",
        "    Default: dev",
        "",
        "Resources:",
        "  # DynamoDB Table",
        "  UsersTable:",
        "    Type: AWS::DynamoDB::Table",
        "    Properties:",
        "      TableName: !Sub 'users-${Environment}'",
        "      BillingMode: PAY_PER_REQUEST",
        "      AttributeDefinitions:",
        "        - AttributeName: userId",
        "          AttributeType: S",
        "      KeySchema:",
        "        - AttributeName: userId",
        "          KeyType: HASH",
        "",
        "  # Lambda Function",
        "  GetUserFunction:",
        "    Type: AWS::Lambda::Function",
        "    Properties:",
        "      FunctionName: !Sub 'get-user-${Environment}'",
        "      Runtime: python3.12",
        "      Handler: index.handler",
        "      MemorySize: 512",
        "      Timeout: 10",
        "      Role: !GetAtt LambdaExecutionRole.Arn",
        "      Environment:",
        "        Variables:",
        "          TABLE_NAME: !Ref UsersTable",
        "",
        "  # IAM Role for Lambda",
        "  LambdaExecutionRole:",
        "    Type: AWS::IAM::Role",
        "    Properties:",
        "      AssumeRolePolicyDocument:",
        "        Version: '2012-10-17'",
        "        Statement:",
        "          - Effect: Allow",
        "            Principal: {Service: lambda.amazonaws.com}",
        "            Action: sts:AssumeRole",
        "      ManagedPolicyArns:",
        "        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        "      Policies:",
        "        - PolicyName: DynamoDBAccess",
        "          PolicyDocument:",
        "            Statement:",
        "              - Effect: Allow",
        "                Action: [dynamodb:GetItem, dynamodb:PutItem]",
        "                Resource: !GetAtt UsersTable.Arn",
        "",
        "Outputs:",
        "  TableName:",
        "    Value: !Ref UsersTable",
        "    Export:",
        "      Name: !Sub '${Environment}-UsersTableName'",
        "```",
        "",
        "```bash",
        "# Deploy:",
        "aws cloudformation deploy \\",
        "  --template-file template.yaml \\",
        "  --stack-name my-app-production \\",
        "  --parameter-overrides Environment=production \\",
        "  --capabilities CAPABILITY_IAM",
        "",
        "# Update (same command — CF detects changes, updates only what changed):",
        "aws cloudformation deploy ...",
        "",
        "# Delete everything:",
        "aws cloudformation delete-stack --stack-name my-app-production",
        "```",
        "",
        "---",
        "",
        "## AWS CDK — CloudFormation with Real Code",
        "",
        "CDK (Cloud Development Kit) lets you define infrastructure in TypeScript, Python,",
        "Java, or Go. It compiles to CloudFormation under the hood.",
        "",
        "**Why CDK over raw CloudFormation?**",
        "```",
        "CloudFormation YAML:                    CDK (TypeScript):",
        "  500 lines of YAML                       100 lines of TypeScript",
        "  No loops, no conditions (limited)       Full programming language features",
        "  No type checking                        TypeScript type safety",
        "  No IDE completion                       Full IDE autocompletion",
        "  Copy-paste for repetition               Loops, functions, abstractions",
        "  Hard to understand structure            Code is self-documenting",
        "```",
        "",
        "```typescript",
        "// AWS CDK TypeScript example",
        "import * as cdk from 'aws-cdk-lib';",
        "import * as lambda from 'aws-cdk-lib/aws-lambda';",
        "import * as apigateway from 'aws-cdk-lib/aws-apigateway';",
        "import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';",
        "",
        "export class MyAppStack extends cdk.Stack {",
        "  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {",
        "    super(scope, id, props);",
        "",
        "    // DynamoDB Table",
        "    const table = new dynamodb.Table(this, 'UsersTable', {",
        "      partitionKey: { name: 'userId', type: dynamodb.AttributeType.STRING },",
        "      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,",
        "      removalPolicy: cdk.RemovalPolicy.RETAIN,  // don't delete on stack delete",
        "    });",
        "",
        "    // Lambda Function",
        "    const getUser = new lambda.Function(this, 'GetUser', {",
        "      runtime: lambda.Runtime.PYTHON_3_12,",
        "      handler: 'index.handler',",
        "      code: lambda.Code.fromAsset('src/handlers/get-user'),",
        "      memorySize: 512,",
        "      timeout: cdk.Duration.seconds(10),",
        "      environment: {",
        "        TABLE_NAME: table.tableName,",
        "      },",
        "    });",
        "",
        "    // Grant Lambda access to table (CDK generates least-privilege IAM policy)",
        "    table.grantReadData(getUser);",
        "",
        "    // API Gateway",
        "    const api = new apigateway.RestApi(this, 'UsersApi');",
        "    api.root",
        "      .addResource('users')",
        "      .addResource('{userId}')",
        "      .addMethod('GET', new apigateway.LambdaIntegration(getUser));",
        "  }",
        "}",
        "```",
        "",
        "```bash",
        "cdk synth   # compile to CloudFormation YAML (review it)",
        "cdk diff    # show what would change if deployed",
        "cdk deploy  # deploy to AWS",
        "cdk destroy # tear down all resources in stack",
        "```",
        "",
        "---",
        "",
        "## Design Exercise: Serverless URL Shortener",
        "",
        "Design a URL shortener (like bit.ly) using serverless AWS services.",
        "This is a classic AWS design interview question.",
        "",
        "```",
        "Requirements:",
        "  POST /shorten  body: {longUrl: 'https://...'} -> returns {shortCode: 'abc123'}",
        "  GET  /{code}   -> 301 redirect to original URL",
        "",
        "Architecture:",
        "",
        "  Client",
        "    |",
        "    v",
        "  API Gateway (HTTP API)",
        "    |",
        "    +--- POST /shorten ---> Lambda: ShortenUrl",
        "    |                           |",
        "    |                       DynamoDB: put item",
        "    |                           {shortCode: 'abc123', longUrl: '...', ttl: ...}",
        "    |                           Return {shortCode: 'abc123'}",
        "    |",
        "    +--- GET /{code} ----> Lambda: RedirectUrl",
        "                               |",
        "                           DynamoDB: get item by shortCode",
        "                           Return 301 Location: longUrl",
        "",
        "Design decisions:",
        "  Short code generation:",
        "    Option A: hash(longUrl) -> take first 6 chars of MD5",
        "    Option B: base62(auto-increment counter in DynamoDB atomic counter)",
        "    Option C: random 6-char alphanumeric, check for collisions",
        "",
        "  DynamoDB schema:",
        "    PK: shortCode (partition key)",
        "    Attributes: longUrl, createdAt, userId, clickCount",
        "    TTL attribute: auto-expire codes after 1 year",
        "",
        "  CDK stack includes:",
        "    DynamoDB table (PAY_PER_REQUEST, TTL enabled)",
        "    2 Lambda functions (ShortenUrl, RedirectUrl)",
        "    API Gateway HTTP API (2 routes)",
        "    Lambda execution roles (least privilege DynamoDB access)",
        "    CloudWatch alarms (error rate > 1%)",
        "```",
        "",
        "---",
        "",
        "## X-Ray — Distributed Tracing",
        "",
        "```",
        "X-Ray traces requests as they flow through your distributed system.",
        "Without X-Ray: 'My API is slow, but which Lambda / which DynamoDB call?'",
        "With X-Ray: see a timeline of every service hop with durations.",
        "",
        "  API Gateway (5ms)",
        "    |",
        "    v",
        "  Lambda: GetUser (250ms total)",
        "    |",
        "    +-- DynamoDB GetItem (45ms)  <- this is slow!",
        "    +-- ElastiCache Get (2ms)",
        "    +-- Processing (200ms)",
        "",
        "Enable in Lambda:",
        "  In CDK:  tracing: lambda.Tracing.ACTIVE",
        "  In SAM:  Tracing: Active",
        "",
        "Adds subsegments automatically for AWS SDK calls.",
        "Add custom subsegments for expensive business logic.",
        "View traces in AWS Console -> X-Ray -> Service Map.",
        "```",
        "",
        "---",
        "",
        "## Secrets Manager and Parameter Store",
        "",
        "```",
        "Never hardcode secrets in Lambda environment variables or code.",
        "",
        "AWS SECRETS MANAGER:",
        "  Store: DB passwords, API keys, certificates",
        "  Automatic rotation: rotates RDS passwords automatically",
        "  Access: Lambda fetches secret at runtime",
        "  Cost: $0.40/secret/month + API calls",
        "",
        "  # Lambda (Python) example:",
        "  import boto3, json",
        "  client = boto3.client('secretsmanager')",
        "  secret = json.loads(client.get_secret_value(",
        "      SecretId='prod/myapp/db-password',",
        "  )['SecretString'])",
        "  DB_PASSWORD = secret['password']",
        "",
        "  Cache secrets in Lambda global scope (fetched once per cold start).",
        "",
        "AWS SYSTEMS MANAGER PARAMETER STORE:",
        "  Store: non-sensitive config that needs versioning",
        "  SecureString tier: encrypted with KMS",
        "  Free for standard parameters",
        "  Use for: feature flags, config values, environment-specific settings",
        "",
        "WHEN TO USE WHICH:",
        "  Secrets Manager: actual secrets (passwords, API keys) + auto-rotation",
        "  Parameter Store: config values, feature flags, non-secret strings",
        "```",
        "",
        "---",
        "",
        "## VPC Lambda — When and Why",
        "",
        "```",
        "By default, Lambda runs OUTSIDE your VPC and cannot access:",
        "  - RDS in private subnet",
        "  - ElastiCache in private subnet",
        "  - Other private resources",
        "",
        "VPC Lambda: attach Lambda to your VPC subnets",
        "  Lambda can now reach private resources inside the VPC",
        "  Lambda gets an ENI (Elastic Network Interface) in your subnet",
        "",
        "TRADE-OFF:",
        "  VPC Lambda: can reach RDS, ElastiCache",
        "  Non-VPC Lambda: faster cold start, can reach internet directly",
        "",
        "VPC Lambda cold starts: used to be much slower (ENI creation)",
        "AWS fixed this in 2019 — VPC Lambda cold starts now similar to non-VPC",
        "",
        "CONFIGURATION:",
        "  Lambda -> Configuration -> VPC",
        "  Select VPC, private subnets, security group",
        "  Security group: must allow outbound to RDS security group on port 5432",
        "  RDS security group: must ALLOW inbound from Lambda security group",
        "",
        "CDK example:",
        "  const fn = new lambda.Function(this, 'MyFn', {",
        "    vpc: myVpc,",
        "    vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },",
        "    securityGroups: [lambdaSg],",
        "    ... other props",
        "  })",
        "```",
        "",
        "---",
        "",
        "## Mind Map",
        "",
        "```",
        "AWS MASTERY",
        "|",
        "+-- LAMBDA ADVANCED",
        "|   +-- Memory = CPU (proportional)",
        "|   +-- Sync / Async / Stream invocation types",
        "|   +-- Reserved vs Provisioned concurrency",
        "|   +-- Execution context reuse (global scope)",
        "|   +-- VPC Lambda (private resource access)",
        "|",
        "+-- API GATEWAY",
        "|   +-- REST API (full features, expensive)",
        "|   +-- HTTP API (simpler, 70% cheaper)",
        "|   +-- Authorisation: JWT, Lambda, IAM, Cognito",
        "|   +-- Request/response flow and event structure",
        "|",
        "+-- CLOUDFORMATION",
        "|   +-- YAML/JSON template declares resources",
        "|   +-- Parameters, Outputs, !Ref, !GetAtt",
        "|   +-- Stacks: create / update / delete atomically",
        "|",
        "+-- CDK",
        "|   +-- TypeScript/Python/Java -> CloudFormation",
        "|   +-- Type safety, IDE support, real code constructs",
        "|   +-- cdk synth / diff / deploy / destroy",
        "|   +-- grantReadData = least-privilege auto-IAM",
        "|",
        "+-- OBSERVABILITY",
        "|   +-- X-Ray (distributed tracing)",
        "|   +-- CloudWatch (metrics, logs, alarms)",
        "|",
        "+-- SECRETS",
        "    +-- Secrets Manager (passwords + rotation)",
        "    +-- Parameter Store (config + feature flags)",
        "```",
        "",
        "---",
        "",
        "## How AWS Mastery Connects to Other Topics",
        "",
        "- **Serverless Patterns**: This topic adds depth to Lambda + API Gateway coverage.",
        "  CDK/CloudFormation is how you actually deploy those patterns.",
        "- **CI/CD**: CDK deploy wired into your CI/CD pipeline = GitOps for AWS infrastructure.",
        "- **Security**: IAM roles for Lambda, Secrets Manager, VPC isolation — all security fundamentals.",
        "- **Docker/K8s**: CDK also deploys ECS Fargate and EKS — the same IaC approach applies.",
        "",
        "---",
        "",
        "## References and Further Learning",
        "",
        "### Videos (Watch These!)",
        "- **AWS CDK Course for Beginners** by freeCodeCamp:",
        "  https://www.youtube.com/watch?v=T-H4nJQyMig",
        "  - 3 hours. Build real infrastructure with CDK TypeScript.",
        "- **API Gateway + Lambda Deep Dive** by Be A Better Dev:",
        "  https://www.youtube.com/watch?v=M91vXdjve7A",
        "  - REST vs HTTP API comparison, authorisers, performance.",
        "",
        "### Free Books and Articles",
        "- **AWS CDK Official Workshop**: https://cdkworkshop.com/",
        "  - Interactive CDK tutorial. Build a complete serverless app step by step.",
        "- **The CDK Book** (free chapter): https://thecdkbook.com/",
        "- **AWS Well-Architected Serverless Lens**: https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/",
        "",
        "### Practice",
        "- **Build a Serverless URL Shortener** — implement the design exercise in this guide.",
        "- **CDK Patterns**: https://cdkpatterns.com/ — ready-made CDK patterns for common architectures.",
    ])

    NEW_Q = [
        {"id":"aws-mastery-q1","type":"mcq","prompt":"In Lambda, what is the relationship between memory and CPU?",
         "choices":["CPU and memory are configured independently","There is no CPU — Lambda is memory only","CPU scales proportionally with memory — more memory = more vCPU. 128MB ≈ 0.125 vCPU, 1024MB ≈ 1 vCPU",
                    "CPU is fixed at 1 vCPU regardless of memory"],
         "answerIndex":2,"explanation":"Lambda has no separate CPU setting. Allocate more memory and you get proportionally more CPU. Often doubling memory reduces duration enough that cost stays the same or decreases while performance doubles.","tags":["lambda","performance","memory"]},
        {"id":"aws-mastery-q2","type":"mcq","prompt":"What is the difference between synchronous and asynchronous Lambda invocation?",
         "choices":["No difference in practice","Sync: caller waits for response, gets error immediately on failure. Async: caller returns immediately, Lambda retries 2x on failure, DLQ captures final failures",
                    "Async is always faster","Sync invocations don't support retry"],
         "answerIndex":1,"explanation":"API Gateway -> Lambda: synchronous (caller waits). S3/SNS/EventBridge -> Lambda: asynchronous (event source doesn't wait). Async adds 2 automatic retries and DLQ support. Choose based on whether the caller needs a real-time response.","tags":["lambda","invocation-types"]},
        {"id":"aws-mastery-q3","type":"mcq","prompt":"What is the key advantage of AWS CDK over raw CloudFormation YAML?",
         "choices":["CDK is faster to deploy","CDK uses a real programming language (TypeScript/Python/Java) enabling loops, functions, type safety, and IDE autocompletion — making complex infra manageable",
                    "CDK doesn't use CloudFormation","CDK is always cheaper"],
         "answerIndex":1,"explanation":"CDK compiles to CloudFormation under the hood but lets you write real code. 500-line CloudFormation YAML becomes 100-line TypeScript. Use loops to create 5 identical resources. Use functions for reusable patterns. IDE catches type errors before deployment.","tags":["cdk","cloudformation","iac"]},
        {"id":"aws-mastery-q4","type":"mcq","prompt":"What does `table.grantReadData(lambdaFn)` do in CDK?",
         "choices":["Copies table data to Lambda","Creates a CloudWatch alarm","Automatically generates an IAM policy granting the Lambda role minimum DynamoDB read permissions on that specific table",
                    "Configures DynamoDB Streams"],
         "answerIndex":2,"explanation":"CDK's grant methods implement least privilege automatically. grantReadData creates a policy allowing only GetItem, Query, Scan on that table. No need to write IAM JSON by hand. CDK knows what permissions each action requires.","tags":["cdk","iam","least-privilege"]},
        {"id":"aws-mastery-q5","type":"mcq","prompt":"What is the difference between REST API and HTTP API in API Gateway?",
         "choices":["REST API is HTTP, HTTP API is WebSocket","REST API: full features (API keys, usage plans, transformations, WAF). HTTP API: simpler, 70% cheaper, JWT auth. Use HTTP API unless you need REST API features.",
                    "They are identical","REST API only works with Lambda"],
         "answerIndex":1,"explanation":"HTTP API launched in 2019: lower latency, 70% cheaper, supports JWT authorisers and Lambda proxy. Missing: API keys, usage plans, request/response transformation, per-method throttling. Use HTTP API as default for new projects.","tags":["api-gateway","rest-api","http-api"]},
        {"id":"aws-mastery-q6","type":"mcq","prompt":"Why would you attach a Lambda function to a VPC?",
         "choices":["VPC Lambda always runs faster","To access private resources in the VPC — RDS databases, ElastiCache caches, internal services — that have no public internet endpoint",
                    "VPC Lambda is required for all production functions","To reduce Lambda costs"],
         "answerIndex":1,"explanation":"Non-VPC Lambda runs outside your VPC. It can hit public internet but not your private RDS or ElastiCache. VPC Lambda gets a network interface in your private subnet, enabling access to private resources. Cold starts are now similar to non-VPC.","tags":["lambda","vpc","networking"]},
        {"id":"aws-mastery-q7","type":"mcq","prompt":"What does `cdk diff` do?",
         "choices":["Shows git diff for CDK files","Shows what AWS resource changes WOULD be made if you ran cdk deploy — without actually deploying",
                    "Compares two CDK stacks","Rolls back the last deployment"],
         "answerIndex":1,"explanation":"cdk diff is like git diff but for infrastructure. It compares your current CDK code against what is deployed and shows: resources to add, modify, or delete. Always run cdk diff before cdk deploy in production.","tags":["cdk","safety"]},
        {"id":"aws-mastery-q8","type":"mcq","prompt":"What is AWS X-Ray used for?",
         "choices":["Security vulnerability scanning","Distributed tracing — shows the request journey across Lambda, DynamoDB, API Gateway with timing for each segment to identify bottlenecks",
                    "Monitoring billing","Log aggregation"],
         "answerIndex":1,"explanation":"X-Ray traces requests end-to-end. Instead of 'my API is slow', you see: API Gateway 5ms -> Lambda 250ms (DynamoDB 45ms + processing 200ms). Identify the slow subsegment. Enable with Tracing: Active in Lambda config.","tags":["x-ray","observability","tracing"]},
        {"id":"aws-mastery-q9","type":"mcq","prompt":"When should you use Secrets Manager over Parameter Store?",
         "choices":["Secrets Manager is always better","Secrets Manager for sensitive secrets that need automatic rotation (RDS passwords, API keys). Parameter Store for non-sensitive config, feature flags, app settings (free, simpler).",
                    "Parameter Store for all secrets","They serve identical purposes"],
         "answerIndex":1,"explanation":"Secrets Manager: $0.40/secret/month, supports automatic rotation of RDS passwords. Parameter Store: free for standard tier, simpler, no rotation. Use Secrets Manager for passwords/tokens that rotate. Parameter Store for DB hostnames, feature flags, config.","tags":["secrets-manager","parameter-store","security"]},
        {"id":"aws-mastery-q10","type":"mcq","prompt":"What does CloudFormation's !Ref intrinsic function do?",
         "choices":["Creates a reference to an external API","Returns the physical ID or value of a resource — used to pass resource identifiers (table name, ARN) to other resources in the same template",
                    "Imports a module","Makes an HTTP request"],
         "answerIndex":1,"explanation":"!Ref UsersTable returns the DynamoDB table name. !GetAtt UsersTable.Arn returns the ARN. These are CF intrinsic functions for wiring resources together without hardcoding. Dynamic references that resolve at deploy time.","tags":["cloudformation","intrinsic-functions"]},
        {"id":"aws-mastery-q11","type":"mcq","prompt":"In a serverless URL shortener, where should you store the short code to long URL mapping?",
         "choices":["In Lambda global variables (in-memory)","In S3 as JSON files","In DynamoDB with shortCode as partition key — fast key-value lookups, scales to billions of records, pay per request",
                    "In RDS with a URLs table"],
         "answerIndex":2,"explanation":"URL shortener: simple key-value lookup (shortCode -> longUrl). DynamoDB PK=shortCode. GetItem = single-digit ms at any scale. No JOINs needed. Enable TTL to auto-expire old codes. No EC2/RDS to manage. Perfect DynamoDB use case.","tags":["dynamodb","architecture","design"]},
        {"id":"aws-mastery-q12","type":"mcq","prompt":"What is the purpose of the Lambda execution context reuse principle?",
         "choices":["Reduces Lambda costs by sharing containers","Allows expensive initialisation (DB connections, SDK clients, secret fetching) to run once per cold start and be reused across many warm invocations",
                    "Enables Lambda to share state with other functions","Reduces memory usage"],
         "answerIndex":1,"explanation":"Code outside the handler function runs once on cold start. Code inside runs per invocation. DB connection outside = one connection per container, reused. DB connection inside = new connection every request (very slow). Global scope is for expensive-to-create, safe-to-reuse objects.","tags":["lambda","performance","context-reuse"]},
        {"id":"aws-mastery-q13","type":"mcq","prompt":"What are CloudFormation Outputs used for?",
         "choices":["Print debug information","Export resource values (ARNs, names, URLs) from a stack for use by other stacks or to display after deployment",
                    "Define stack parameters","Rollback configuration"],
         "answerIndex":1,"explanation":"Outputs export values from a stack. Other stacks import them with Fn::ImportValue. Example: network stack exports VPC ID and subnet IDs. Application stack imports them. Enables modular multi-stack architectures without duplicating resource definitions.","tags":["cloudformation","outputs","cross-stack"]},
        {"id":"aws-mastery-q14","type":"mcq","prompt":"In API Gateway, what is a Lambda Authoriser?",
         "choices":["A Lambda function that handles all requests","A Lambda function that validates bearer tokens or headers and returns an IAM policy allowing or denying the request — enables custom auth logic",
                    "An IAM role for API Gateway","A CloudWatch alarm for API quotas"],
         "answerIndex":1,"explanation":"Lambda Authoriser: API Gateway calls your auth Lambda with the token. Lambda validates it (verify JWT signature, call a user database, check an internal auth service) and returns Allow or Deny. Cached for performance. Use for custom auth not covered by built-in JWT/Cognito.","tags":["api-gateway","authorisation","lambda"]},
        {"id":"aws-mastery-q15","type":"mcq","prompt":"What does `cdk synth` produce?",
         "choices":["Python bytecode","A CloudFormation template (YAML) from your CDK code — review it before deploying to understand exactly what AWS resources will be created",
                    "A Docker image","A test report"],
         "answerIndex":1,"explanation":"cdk synth compiles your CDK TypeScript/Python to a CloudFormation template. This is what gets deployed. Running synth and reviewing the output is how you verify CDK is generating the correct resources and IAM policies.","tags":["cdk","cloudformation"]},
        {"id":"aws-mastery-q16","type":"mcq","prompt":"What is Lambda Reserved Concurrency?",
         "choices":["Pre-warmed containers","A concurrency setting that both GUARANTEES a minimum and CAPS a maximum — the function cannot exceed this concurrency, protecting downstream resources",
                    "Maximum concurrent Lambda requests across account","Free Lambda tier allocation"],
         "answerIndex":1,"explanation":"Reserved Concurrency = N means: (1) this function always has N concurrency available (not stolen by other functions), AND (2) this function cannot exceed N. Cap your payment Lambda at 20 to prevent overwhelming the payment API with 20+ simultaneous requests.","tags":["lambda","concurrency","reserved"]},
        {"id":"aws-mastery-q17","type":"mcq","prompt":"In CloudFormation, what happens when a stack update fails?",
         "choices":["Partial update remains in place","CloudFormation rolls back ALL changes in the update — restores every resource to its previous state automatically",
                    "Stack is deleted","You must manually roll back"],
         "answerIndex":1,"explanation":"CloudFormation updates are transactional. If any resource update fails, CF rolls back all changes in that update. Your infrastructure returns to the last known-good state. This is why CF is safer than running individual API calls that can leave infra in inconsistent states.","tags":["cloudformation","rollback","reliability"]},
        {"id":"aws-mastery-q18","type":"mcq","prompt":"What does `CAPABILITY_IAM` flag mean in CloudFormation deploy commands?",
         "choices":["Enables IAM user creation only","Acknowledges that the template creates or modifies IAM resources (roles, policies) — required as a safety confirmation to prevent accidental privilege escalation",
                    "Grants admin IAM access","Required for all deployments"],
         "answerIndex":1,"explanation":"CloudFormation requires explicit acknowledgement when creating IAM resources because misconfigured IAM can grant excessive permissions. --capabilities CAPABILITY_IAM tells CF: 'Yes, I understand this template creates IAM resources, proceed.'","tags":["cloudformation","iam","safety"]},
        {"id":"aws-mastery-q19","type":"mcq","prompt":"What is the purpose of DynamoDB TTL (Time to Live)?",
         "choices":["TTL controls DynamoDB performance","TTL automatically deletes items after a specified timestamp — no cost for deletion, no Lambda needed, great for session data, caches, expired short URLs",
                    "TTL limits DynamoDB table size","TTL is for DynamoDB Global Tables"],
         "answerIndex":1,"explanation":"Enable TTL on a timestamp attribute. Items with that attribute set to a past Unix timestamp are automatically deleted within 48 hours. No cost for TTL deletions. Perfect for: session tokens, short URL expiration, cache invalidation, event logs.","tags":["dynamodb","ttl","data-management"]},
        {"id":"aws-mastery-q20","type":"mcq","prompt":"What is a CloudFormation Stack?",
         "choices":["A list of AWS regions","A collection of AWS resources managed as a unit — created, updated, and deleted together. One template = one stack.",
                    "A Lambda deployment package","An S3 bucket for CloudFormation templates"],
         "answerIndex":1,"explanation":"A stack is a collection of resources that are created and managed together. Deploying a template creates a stack. Update the template = update the stack (CF handles change detection). Delete the stack = deletes all resources in it (including data — be careful!).","tags":["cloudformation","stacks"]},
    ]

    NEW_FC = [
        {"id":"aws-mastery-fc1","front":"CDK workflow commands","back":"cdk synth (compile to CF YAML, review) -> cdk diff (see what changes) -> cdk deploy (apply changes). Always diff before deploy in prod. cdk destroy = delete entire stack (including databases if not RETAIN).","tags":["cdk","workflow"]},
        {"id":"aws-mastery-fc2","front":"Lambda cold start mitigation order","back":"1. Smaller package (deps in Layers)  2. Python/Node over Java  3. Provisioned Concurrency (pre-warm, costs $)  4. Ping with EventBridge (free)  5. GraalVM native for Java  6. Use HTTP API (lower overhead than REST API)","tags":["lambda","cold-start"]},
        {"id":"aws-mastery-fc3","front":"API Gateway: REST API vs HTTP API","back":"HTTP API: default choice. 70% cheaper, lower latency, JWT auth, CORS, Lambda proxy. REST API: only when you need API keys/usage plans, per-method auth, request/response transformation, WAF at API level.","tags":["api-gateway","rest-api","http-api"]},
        {"id":"aws-mastery-fc4","front":"CloudFormation atomic rollback","back":"Stack update fails -> CF rolls back ALL changes in that update atomically. Infrastructure returns to last known-good state. This is why IaC > manual API calls for production.","tags":["cloudformation","reliability"]},
        {"id":"aws-mastery-fc5","front":"Serverless URL shortener design","back":"DynamoDB (PK=shortCode, TTL=expiry). HTTP API + 2 Lambda functions (shorten, redirect). ShortenUrl: generate base62 code, write to DynamoDB, return short URL. RedirectUrl: GetItem by code, return 301 Location header.","tags":["design","dynamodb","lambda"]},
        {"id":"aws-mastery-fc6","front":"Lambda global scope rule","back":"OUTSIDE handler: initialise once (DB client, secrets, large config). Reused across warm invocations = good. INSIDE handler: per-request state only (user-specific data, request context). NEVER store user data globally.","tags":["lambda","context-reuse"]},
        {"id":"aws-mastery-fc7","front":"Secrets Manager vs Parameter Store","back":"Secrets Manager: passwords + API keys + auto-rotation support. $0.40/secret/month. Parameter Store: config + feature flags. Free (standard tier). Use SM for actual secrets, SSM PS for config. Both much better than env vars in Lambda.","tags":["secrets","security"]},
        {"id":"aws-mastery-fc8","front":"X-Ray tracing — enable and use","back":"CDK: tracing: lambda.Tracing.ACTIVE. SAM: Tracing: Active. Automatically traces AWS SDK calls. Add custom segments with xray.begin_segment(). View in Console -> X-Ray -> Traces or Service Map to find slow subsegments.","tags":["x-ray","observability"]},
    ]

    d['guide'] = GUIDE
    d['questions'] = NEW_Q
    d['flashcards'] = NEW_FC

    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"aws-mastery.json done: guide={len(GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ── patch_serverless.py ──────────────────────────────────────────────────────────────────
    p = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/serverless-patterns.json')
    d = json.loads(p.read_text())

    GUIDE = "\n".join([
        "# Serverless Patterns",
        "",
        "## What Is Serverless? (Start From Zero)",
        "",
        "The word 'serverless' is a bit misleading — there ARE servers, you just don't see them.",
        "What it really means: you write code (functions), upload it, and AWS runs it for you.",
        "You do not provision servers, patch OS, configure capacity, or pay for idle time.",
        "",
        "**Traditional server-based model:**",
        "```",
        "You:  rent an EC2 instance ($50/month)",
        "      configure the OS",
        "      deploy your app",
        "      pay $50 whether it gets 0 or 1 million requests",
        "      scale manually when traffic grows",
        "      wake up at 3am if the server crashes",
        "```",
        "",
        "**Serverless (Lambda) model:**",
        "```",
        "You:  write a function (50 lines of Python/Java/Node)",
        "      upload to Lambda",
        "      AWS runs it when triggered",
        "      pay ONLY per execution (first million requests/month FREE)",
        "      AWS scales automatically (0 to 10,000 concurrent in seconds)",
        "      AWS handles all failures and restarts",
        "```",
        "",
        "**Analogy:** Serverless is like a taxi vs owning a car.",
        "Owning a car (EC2): pay insurance, maintenance, fuel all the time — even when parked.",
        "Taxi (Lambda): pay only when you actually ride. Perfect for irregular trips.",
        "",
        "---",
        "",
        "## AWS Lambda — The Core Serverless Building Block",
        "",
        "Lambda is a Function-as-a-Service (FaaS). You provide a function, AWS runs it on demand.",
        "",
        "```",
        "Lambda function lifecycle:",
        "",
        "COLD START (first invocation or after idle period):",
        "  1. AWS allocates a container (VM slot)",
        "  2. Downloads your deployment package",
        "  3. Starts the runtime (JVM, Node, Python interpreter)",
        "  4. Runs initialisation code (outside handler)",
        "  5. Runs your handler function",
        "  Total: 100ms - 3 seconds depending on runtime + package size",
        "",
        "WARM INVOCATION (container reused):",
        "  1. Runs your handler function",
        "  Total: your actual code execution time only",
        "",
        "COLD START visual:",
        "  Request ---> [Cold: init container + runtime + code] ---> Response",
        "               |                                      |",
        "               |<-------- 1-3 seconds extra --------->|",
        "",
        "  Request ---> [Warm: just run handler] ---> Response",
        "               |                       |",
        "               |<--- milliseconds ----->|",
        "```",
        "",
        "**Lambda configuration basics:**",
        "```",
        "Memory:    128MB to 10,240MB  (CPU scales proportionally with memory)",
        "Timeout:   1 second to 15 minutes (max)",
        "Runtime:   Python 3.12, Node 20, Java 21, Go, etc.",
        "Package:   .zip file or container image (up to 10GB)",
        "",
        "# Python Lambda handler structure",
        "def handler(event, context):",
        "    # event = the trigger payload (S3 event, API Gateway request, etc.)",
        "    # context = metadata (function name, remaining time, request ID)",
        "",
        "    print(f'Processing event: {event}')",
        "",
        "    result = process(event['data'])",
        "",
        "    return {",
        "        'statusCode': 200,",
        "        'body': json.dumps({'result': result})",
        "    }",
        "```",
        "",
        "---",
        "",
        "## Lambda Triggers — What Can Invoke a Lambda?",
        "",
        "```",
        "Lambda is event-driven — something must trigger it.",
        "",
        "+------------------+--------------------------------------------+",
        "| Trigger          | Use case                                   |",
        "+------------------+--------------------------------------------+",
        "| API Gateway      | HTTP endpoint -> Lambda = REST API         |",
        "| S3               | File uploaded -> Lambda processes it       |",
        "| SQS              | Message in queue -> Lambda consumes it     |",
        "| SNS              | Notification published -> Lambda receives  |",
        "| DynamoDB Streams | DB record changed -> Lambda reacts         |",
        "| EventBridge      | Scheduled (cron) or custom events          |",
        "| Cognito          | User sign-up -> Lambda validates/enriches  |",
        "| CloudWatch       | Log pattern matched -> Lambda alerts       |",
        "+------------------+--------------------------------------------+",
        "",
        "PATTERN 1: HTTP API",
        "  Browser -> API Gateway -> Lambda -> DynamoDB -> Response",
        "",
        "PATTERN 2: File processing",
        "  Upload image to S3 -> S3 triggers Lambda -> Lambda resizes image -> saves to S3",
        "",
        "PATTERN 3: Queue worker",
        "  API writes message to SQS -> Lambda polls SQS -> Lambda processes message",
        "  (decoupled, retryable, handles bursts via queue buffering)",
        "",
        "PATTERN 4: Scheduled job",
        "  EventBridge cron: '0 2 * * *' -> Lambda runs daily at 2am -> sends report emails",
        "```",
        "",
        "---",
        "",
        "## API Gateway + Lambda — Building a REST API",
        "",
        "This is the most common serverless pattern: replace a traditional server with",
        "API Gateway (HTTP router) + Lambda (business logic).",
        "",
        "```",
        "Traditional:               Serverless:",
        "  EC2 running Spring Boot    API Gateway + Lambda",
        "  Always on = always paying  Pay per request",
        "  Manual scaling             Auto-scales to millions",
        "  You manage OS/runtime      Zero ops",
        "",
        "Architecture:",
        "  Client",
        "    |",
        "    | HTTPS request",
        "    v",
        "  API Gateway",
        "    | matches route: GET /users/{id}",
        "    v",
        "  Lambda function: getUserById",
        "    | queries",
        "    v",
        "  DynamoDB",
        "    |",
        "    v (response bubbles back up)",
        "  Client receives JSON response",
        "",
        "Terraform / SAM / CDK define both API Gateway and Lambda together.",
        "```",
        "",
        "---",
        "",
        "## Cold Start Problem — Causes and Solutions",
        "",
        "```",
        "WHY COLD STARTS HAPPEN:",
        "  Lambda containers are created on first request and reused for ~15 min.",
        "  After 15 min idle, container is recycled.",
        "  Next request creates a new container -> cold start again.",
        "",
        "COLD START DURATION BY RUNTIME:",
        "  Python/Node.js:  ~100-300ms   (fast startup, small runtime)",
        "  Java (JVM):      ~1-3 seconds (JVM startup is slow!)",
        "  Container image: up to 5-10s  (larger image = slower pull)",
        "",
        "SOLUTIONS:",
        "",
        "1. PROVISIONED CONCURRENCY:",
        "   Tell Lambda to keep N containers warm at all times.",
        "   Cost: you pay for idle warm containers.",
        "   Use for: user-facing APIs where latency matters.",
        "",
        "2. KEEP-ALIVE PING:",
        "   Schedule EventBridge to invoke Lambda every 5 minutes.",
        "   Free (Lambda gets ~1M free invocations/month).",
        "   Use for: low-traffic functions that must be fast occasionally.",
        "",
        "3. PACKAGE SIZE OPTIMISATION:",
        "   Smaller .zip = faster cold start.",
        "   Only include needed libraries.",
        "   Use Lambda Layers for shared dependencies.",
        "   Java: use GraalVM native image (compiles to native binary, no JVM startup).",
        "",
        "4. CHOOSE FAST RUNTIME:",
        "   For latency-sensitive APIs: Node.js or Python over Java.",
        "   Java is great for CPU-heavy batch work where cold start % is small.",
        "",
        "5. MEMORY SIZE:",
        "   More RAM = more CPU = faster init + execution.",
        "   1024MB often sweet spot: 2x memory, still cheaper than EC2.",
        "```",
        "",
        "---",
        "",
        "## Step Functions — Orchestrating Multiple Lambdas",
        "",
        "When your workflow needs multiple steps, conditional logic, retries, and parallelism,",
        "chaining Lambda A -> Lambda B in code is fragile.",
        "Step Functions is a visual state machine for orchestrating workflows.",
        "",
        "```",
        "WITHOUT Step Functions (Lambda chaining):",
        "  Lambda A calls Lambda B calls Lambda C",
        "  Problems:",
        "    - If Lambda B fails, who retries?",
        "    - If Lambda A times out waiting for B, what happens?",
        "    - How do you see what step failed?",
        "    - Nested timeouts: 15min max chains are hard",
        "",
        "WITH Step Functions:",
        "  Define states in JSON (Amazon States Language)",
        "  Step Functions engine manages transitions, retries, timeouts",
        "  Visual flow diagram in AWS Console",
        "  Full audit trail: see every step, input/output, error",
        "",
        "Example: Order Processing Workflow:",
        "  [ValidateOrder]",
        "       |",
        "  [ChargePayment] -- FAIL -> [RefundPayment]",
        "       |",
        "  [ReserveInventory] -- FAIL -> [RefundPayment]",
        "       |",
        "  [SendConfirmationEmail]",
        "       |",
        "  [Done]",
        "",
        "Each box is a Lambda function. Step Functions handles:",
        "  - Executing each step",
        "  - Catching errors (Catch states)",
        "  - Retrying with exponential backoff (Retry states)",
        "  - Parallel branches (Parallel state)",
        "  - Waiting for external events (Wait for Token pattern)",
        "```",
        "",
        "---",
        "",
        "## EventBridge — Cloud Event Bus",
        "",
        "```",
        "EventBridge is a serverless event bus — it routes events between services.",
        "",
        "SCHEDULED EVENTS (cron):",
        "  EventBridge rule: rate(1 hour) or cron(0 2 * * ? *)",
        "  Action: invoke Lambda function",
        "  Use: scheduled reports, cleanup jobs, notifications",
        "",
        "CUSTOM EVENTS (event-driven architecture):",
        "  Service A publishes event: {source: 'orders', detail-type: 'OrderPlaced', detail: {...}}",
        "  Rules match on event fields",
        "  Multiple targets can receive same event:",
        "    -> Lambda: process fraud check",
        "    -> SQS: queue for email service",
        "    -> Step Functions: start workflow",
        "",
        "Benefits:",
        "  - Services don't need to know about each other (loose coupling)",
        "  - Add new consumers without modifying publishers",
        "  - Built-in retry with DLQ (dead letter queue)",
        "  - Schema registry to document event shapes",
        "```",
        "",
        "---",
        "",
        "## Lambda Best Practices",
        "",
        "```",
        "1. KEEP FUNCTIONS SMALL AND SINGLE-PURPOSE:",
        "   One Lambda = one responsibility.",
        "   getUserById, processPayment, sendEmail — separate functions.",
        "   Not: doEverything.",
        "",
        "2. STORE STATE EXTERNALLY:",
        "   Lambda is stateless — containers can be recycled any time.",
        "   Store state in DynamoDB, S3, ElastiCache — NOT in Lambda global variables.",
        "   Global variables persist ACROSS warm invocations — can cause bugs!",
        "   (Exception: connection pooling: keep DB connection in global = fine.)",
        "",
        "3. SET APPROPRIATE TIMEOUT:",
        "   Default: 3 seconds. Know your max expected execution time.",
        "   Too low = functions killed mid-execution.",
        "   Too high = runaway functions run up your bill.",
        "",
        "4. ENVIRONMENT VARIABLES FOR CONFIG:",
        "   DB_URL, TABLE_NAME, REGION — never hardcode.",
        "   Use Systems Manager Parameter Store or Secrets Manager for secrets.",
        "",
        "5. USE LAMBDA LAYERS FOR SHARED CODE:",
        "   Common libraries (pandas, numpy, shared utils) as a Layer.",
        "   Multiple functions share one Layer — update once, applies everywhere.",
        "",
        "6. IDEMPOTENCY:",
        "   Lambda can be invoked more than once for the same event (retries).",
        "   Your handler must produce same result if called twice.",
        "   Use idempotency keys: check if already processed before doing work.",
        "",
        "7. DEAD LETTER QUEUES (DLQ):",
        "   Configure SQS or SNS as DLQ for failed Lambda invocations.",
        "   Failed events are not lost — they go to DLQ for investigation/replay.",
        "```",
        "",
        "---",
        "",
        "## Serverless Application Model (SAM)",
        "",
        "```",
        "SAM is AWS's framework for building serverless apps locally and deploying them.",
        "It extends CloudFormation with serverless-specific resources.",
        "",
        "# template.yaml",
        "AWSTemplateFormatVersion: '2010-09-09'",
        "Transform: AWS::Serverless-2016-10-31",
        "",
        "Resources:",
        "  GetUserFunction:",
        "    Type: AWS::Serverless::Function",
        "    Properties:",
        "      Handler: src/handlers/getUser.handler",
        "      Runtime: python3.12",
        "      MemorySize: 512",
        "      Timeout: 10",
        "      Events:",
        "        GetUser:",
        "          Type: Api",
        "          Properties:",
        "            Path: /users/{id}",
        "            Method: GET",
        "      Environment:",
        "        Variables:",
        "          USERS_TABLE: !Ref UsersTable",
        "",
        "  UsersTable:",
        "    Type: AWS::Serverless::SimpleTable",
        "    Properties:",
        "      PrimaryKey:",
        "        Name: userId",
        "        Type: String",
        "",
        "# Commands:",
        "sam build              # build deployment package",
        "sam local invoke       # test Lambda locally",
        "sam local start-api    # run API Gateway locally on port 3000",
        "sam deploy --guided    # deploy to AWS",
        "```",
        "",
        "---",
        "",
        "## Serverless vs Containers vs EC2 — When to Use Each",
        "",
        "```",
        "+------------------+----------------------+----------------------------+",
        "| Factor           | Lambda (Serverless)  | Container/EC2              |",
        "+------------------+----------------------+----------------------------+",
        "| Startup time     | 100ms-3s cold start  | Always warm                |",
        "| Max runtime      | 15 minutes           | Unlimited                  |",
        "| Cost model       | Per request          | Per hour (even idle)       |",
        "| State            | Stateless            | Can be stateful            |",
        "| Cold start       | Yes (mitigable)      | No                         |",
        "| Scaling          | Automatic (fast)     | Manual or HPA (slower)     |",
        "| Ops overhead     | Near zero            | OS patching, monitoring    |",
        "+------------------+----------------------+----------------------------+",
        "",
        "USE LAMBDA WHEN:",
        "  - Sporadic/unpredictable traffic",
        "  - Event-driven triggers (S3 upload, queue message)",
        "  - Short-duration tasks (under 15 min)",
        "  - Rapid prototyping",
        "  - Budget-sensitive (pay per use)",
        "",
        "AVOID LAMBDA WHEN:",
        "  - Long-running jobs (>15 min) -> use ECS Fargate",
        "  - Latency-critical API with consistent traffic -> EC2/ECS cheaper",
        "  - Large ML models that need specialised hardware -> SageMaker",
        "  - Complex stateful workflows -> Step Functions + ECS",
        "```",
        "",
        "---",
        "",
        "## Mind Map",
        "",
        "```",
        "SERVERLESS PATTERNS",
        "|",
        "+-- LAMBDA",
        "|   +-- FaaS: pay per execution",
        "|   +-- Triggers: API GW, S3, SQS, EventBridge, cron",
        "|   +-- Cold start: init overhead (worst on JVM)",
        "|   +-- Handler: event + context -> response",
        "|   +-- Stateless: store state externally",
        "|",
        "+-- API GATEWAY + LAMBDA",
        "|   +-- Replace traditional server",
        "|   +-- Route -> Lambda -> DynamoDB",
        "|   +-- Pay per request, auto-scale",
        "|",
        "+-- STEP FUNCTIONS",
        "|   +-- Orchestrate multi-Lambda workflows",
        "|   +-- Retry/catch/parallel built-in",
        "|   +-- Visual state machine",
        "|",
        "+-- EVENTBRIDGE",
        "|   +-- Event bus: publish/subscribe",
        "|   +-- Scheduled cron -> Lambda",
        "|   +-- Decoupled architecture",
        "|",
        "+-- BEST PRACTICES",
        "|   +-- Single-purpose functions",
        "|   +-- External state (DynamoDB/S3)",
        "|   +-- Idempotent handlers",
        "|   +-- DLQ for failures",
        "|   +-- Lambda Layers for shared code",
        "|",
        "+-- SAM",
        "    +-- template.yaml = Lambda + API Gateway",
        "    +-- sam local = test offline",
        "    +-- sam deploy = ship to AWS",
        "```",
        "",
        "---",
        "",
        "## How Serverless Connects to Other Topics",
        "",
        "- **AWS Mastery**: Lambda is the foundation of AWS serverless. API Gateway +",
        "  Lambda + DynamoDB is the canonical serverless stack.",
        "- **SQS**: Lambda + SQS is one of the most common patterns: queue absorbs bursts,",
        "  Lambda workers consume at controlled concurrency.",
        "- **CI/CD**: SAM/CDK pipelines build and deploy Lambda functions automatically.",
        "- **Docker/Containers**: Lambda also supports container images — bridge between",
        "  serverless and container worlds.",
        "",
        "---",
        "",
        "## Common Beginner Mistakes",
        "",
        "1. **Storing state in Lambda global variables** — persists across warm invocations,",
        "   causes bugs. Exception: DB connection objects are fine to cache globally.",
        "2. **Timeout too short** — Lambda killed mid-execution. Understand your p99 latency.",
        "3. **Huge deployment packages** — 100MB+ packages cause slow cold starts. Tree-shake,",
        "   use Layers, use slim base images.",
        "4. **No DLQ** — failed events silently disappear. Always configure a DLQ.",
        "5. **Chaining Lambdas directly** — use Step Functions for multi-step workflows.",
        "6. **No idempotency** — Lambda retries on failure. Running twice = double charge,",
        "   double email, double insert unless you guard against it.",
        "7. **Ignoring cold starts for Java** — JVM cold start can be 2-3s. Use Provisioned",
        "   Concurrency or switch to Python/Node for latency-sensitive endpoints.",
        "",
        "---",
        "",
        "## References and Further Learning",
        "",
        "### Videos (Watch These!)",
        "- **AWS Lambda Tutorial for Beginners** by TechWorld with Nana:",
        "  https://www.youtube.com/watch?v=eOBq__h4OJ4",
        "  - 1 hour. Lambda architecture, triggers, hands-on demo.",
        "- **Serverless Architecture Explained** by Fireship:",
        "  https://www.youtube.com/watch?v=vxJobGtqKVM",
        "  - 7 minutes. Visual walkthrough of serverless patterns.",
        "",
        "### Free Books and Articles",
        "- **AWS Lambda official docs - Getting Started**:",
        "  https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html",
        "- **Serverless Land** (AWS patterns library): https://serverlessland.com/patterns",
        "  - Real-world serverless patterns with CDK/SAM code. Browse patterns by use case.",
        "",
        "### Diagrams and Cheatsheets",
        "- **Serverless patterns diagram**: https://serverlessland.com/",
        "- **AWS Step Functions visualiser**: https://states-language.net/spec.html",
        "",
        "### Practice",
        "- **AWS Serverless Workshop**: https://s12d.com/workshop",
        "- **Build a Serverless API** (free AWS tutorial): https://aws.amazon.com/getting-started/hands-on/build-serverless-web-app-lambda-apigateway-s3-dynamodb-cognito/",
    ])

    NEW_Q = [
        {"id":"sls-q4","type":"mcq","prompt":"What is a Lambda cold start?",
         "choices":["Lambda crashing permanently","The latency overhead when AWS must initialise a new container, download the code, and start the runtime — happens on first invocation after idle","Lambda running out of memory","Lambda timeout"],
         "answerIndex":1,"explanation":"Cold start = Lambda container provisioning overhead. After ~15 min idle, containers are recycled. Next request pays the cold start tax. Warm invocations (reused container) have no overhead.","tags":["lambda","cold-start"]},
        {"id":"sls-q5","type":"mcq","prompt":"Which runtime has the LONGEST Lambda cold start times?",
         "choices":["Python 3.12","Node.js 20","Java (JVM)","Ruby"],
         "answerIndex":2,"explanation":"JVM startup time (loading classes, JIT compilation) adds 1-3 seconds to Lambda cold starts. Python and Node.js start in ~100-300ms. For latency-sensitive APIs, prefer Python/Node or use Provisioned Concurrency with Java.","tags":["lambda","cold-start","java"]},
        {"id":"sls-q6","type":"mcq","prompt":"What is Provisioned Concurrency in Lambda?",
         "choices":["Maximum number of concurrent Lambda executions","Pre-warming a specified number of Lambda containers so they are always ready — eliminating cold starts at the cost of paying for idle warm containers",
                    "Automatic scaling policy","Reserved Lambda capacity"],
         "answerIndex":1,"explanation":"Provisioned Concurrency keeps N containers initialised and warm. No cold start for requests up to N concurrency. You pay for the warm containers even if no requests come in. Worth it for user-facing latency-critical APIs.","tags":["lambda","provisioned-concurrency"]},
        {"id":"sls-q7","type":"mcq","prompt":"Why must Lambda functions be designed to be idempotent?",
         "choices":["Lambda charges per invocation","Lambda can retry failed invocations — if your handler isn't idempotent, retries cause duplicate actions (double charge, double email, duplicate DB record)",
                    "Lambda has no retry behaviour","Idempotency improves performance"],
         "answerIndex":1,"explanation":"Lambda retries on errors (SQS triggers retry up to maxReceiveCount times). If processPayment() runs twice, customer is charged twice unless you check 'already processed this request ID' first.","tags":["lambda","idempotency"]},
        {"id":"sls-q8","type":"mcq","prompt":"What happens if you store state in a Lambda global variable?",
         "choices":["It is lost after every invocation","It persists across warm invocations of the SAME container — can cause data leakage between unrelated requests",
                    "It causes a cold start","Lambda resets all globals on every call"],
         "answerIndex":1,"explanation":"Lambda containers are reused for warm invocations. A global variable set in request 1 is still there in request 2 on the same container. 'Store DB connection globally' = fine. 'Store user data globally' = data leakage bug.","tags":["lambda","state","gotcha"]},
        {"id":"sls-q9","type":"mcq","prompt":"What is the maximum timeout for a Lambda function?",
         "choices":["30 seconds","5 minutes","15 minutes","1 hour"],
         "answerIndex":2,"explanation":"Lambda maximum timeout is 15 minutes. For longer jobs, use AWS Fargate (ECS tasks) or AWS Batch. Step Functions can coordinate multiple Lambda calls but each individual Lambda still has the 15-min limit.","tags":["lambda","limits"]},
        {"id":"sls-q10","type":"mcq","prompt":"What is the primary benefit of using Step Functions over chaining Lambdas directly?",
         "choices":["Step Functions is cheaper","Step Functions provides built-in state management, retry/catch logic, parallel execution, and a visual audit trail — replacing fragile hand-coded orchestration logic in Lambda",
                    "Step Functions is faster","Step Functions removes the need for Lambda"],
         "answerIndex":1,"explanation":"Hand-coded Lambda chains are brittle: no built-in retry, hard to debug, nested timeouts. Step Functions gives you: Retry with backoff, Catch for error handling, Parallel states, Wait states, and a visual execution history in the console.","tags":["step-functions","orchestration"]},
        {"id":"sls-q11","type":"mcq","prompt":"What is an AWS Lambda Layer?",
         "choices":["A networking concept","A reusable package of shared code or dependencies that multiple Lambda functions can reference — uploaded once, attached to many functions",
                    "Lambda version alias","Cold start optimisation"],
         "answerIndex":1,"explanation":"Layers let you share: libraries (pandas, boto3), custom runtimes, company-wide utilities. Update the Layer once and all attached functions get the update. Keeps deployment packages small (faster cold starts).","tags":["lambda","layers"]},
        {"id":"sls-q12","type":"mcq","prompt":"What is a Dead Letter Queue (DLQ) in serverless context?",
         "choices":["A queue for spam messages","A destination (SQS or SNS) where failed Lambda invocations are sent after all retries are exhausted — prevents event loss",
                    "A Lambda error log","A backup Lambda function"],
         "answerIndex":1,"explanation":"Without DLQ, failed events are silently discarded after retries. With DLQ: failed events go to an SQS queue for investigation, alerting, and manual replay. Always configure DLQ for async Lambda invocations.","tags":["lambda","dlq","reliability"]},
        {"id":"sls-q13","type":"mcq","prompt":"Which AWS service replaces traditional cron jobs in a serverless architecture?",
         "choices":["CloudWatch Logs","AWS Batch","Amazon EventBridge (Scheduler) — triggers Lambda on a cron or rate schedule","SQS FIFO"],
         "answerIndex":2,"explanation":"EventBridge Scheduler (formerly CloudWatch Events) lets you define cron expressions or rates. It triggers Lambda at the scheduled time. No server needed for 'run every day at 2am' tasks.","tags":["eventbridge","scheduling"]},
        {"id":"sls-q14","type":"mcq","prompt":"In SAM (Serverless Application Model), what does `sam local start-api` do?",
         "choices":["Deploys to AWS","Creates API Gateway in AWS","Starts a local HTTP server that simulates API Gateway and invokes your Lambda handler locally — for testing without deploying",
                    "Builds the Docker image"],
         "answerIndex":2,"explanation":"sam local start-api spins up a local API Gateway emulator on port 3000. You can hit it with Postman or curl, and SAM invokes your Lambda handler with the same event structure as real API Gateway — all locally.","tags":["sam","local-development"]},
        {"id":"sls-q15","type":"mcq","prompt":"What is the 'Lambda execution environment' reuse benefit for database connections?",
         "choices":["Lambda automatically manages DB connection pools","You can initialise a DB connection OUTSIDE the handler function — it persists in the warm container and is reused across invocations, avoiding reconnect overhead",
                    "Lambda has built-in connection pooling","There is no benefit"],
         "answerIndex":1,"explanation":"Initialise expensive resources (DB connections, SDK clients) outside the handler function body. They are created once during cold start and reused across warm invocations. This is the ONE case where global state in Lambda is correct.","tags":["lambda","performance","database"]},
        {"id":"sls-q16","type":"mcq","prompt":"What does the `event` parameter in a Lambda handler contain?",
         "choices":["HTTP headers only","Empty by default","The trigger payload — for API Gateway: HTTP request details; for S3: bucket/key info; for SQS: message bodies. Format varies by trigger type.",
                    "Lambda configuration settings"],
         "answerIndex":2,"explanation":"The event object is the trigger's input data. API Gateway event contains httpMethod, path, headers, body. S3 event contains bucket name, object key, event type. SQS event contains an array of messages with their bodies.","tags":["lambda","event","triggers"]},
        {"id":"sls-q17","type":"mcq","prompt":"When would you choose EC2/ECS over Lambda for a workload?",
         "choices":["When requests are sporadic","When you need auto-scaling","When the workload runs longer than 15 minutes, needs consistent low latency under constant traffic, or requires GPU/specialised hardware",
                    "Lambda is always better"],
         "answerIndex":2,"explanation":"Lambda excels at sporadic, short-duration, event-driven work. But: video encoding (hours), ML training (GPU needed), constant high-traffic API (EC2/ECS often cheaper than Lambda at scale) — these are EC2/Fargate territory.","tags":["lambda","vs-containers","trade-offs"]},
        {"id":"sls-q18","type":"multi","prompt":"Which of these are valid Lambda triggers? (Select all that apply)",
         "choices":["HTTP request via API Gateway","File uploaded to S3","Message added to SQS queue","Cron schedule via EventBridge"],
         "answerIndexes":[0,1,2,3],"explanation":"All four are valid Lambda triggers. Lambda is event-driven and integrates with practically every AWS service. You can also trigger it from DynamoDB Streams, SNS, Kinesis, IoT Core, and more.","tags":["lambda","triggers"]},
        {"id":"sls-q19","type":"mcq","prompt":"What is the Lambda concurrency limit and what happens when it is hit?",
         "choices":["No limit","When concurrent executions exceed the account limit (default 1000), new requests get a 429 TooManyRequestsException and are throttled",
                    "Lambda auto-scales infinitely","Requests are queued automatically"],
         "answerIndex":1,"explanation":"Each AWS account has a default concurrency limit (1000 across all Lambdas). When exceeded, new invocations are throttled (429). Request a limit increase via AWS Support or use Reserved Concurrency to guarantee capacity for critical functions.","tags":["lambda","concurrency","limits"]},
        {"id":"sls-q20","type":"mcq","prompt":"What is the 'fan-out' serverless pattern?",
         "choices":["Lambda calling one downstream service","One event triggers multiple parallel Lambda executions — used for parallel processing of different aspects of the same event",
                    "Lambda reading from multiple queues","Step Functions sequential execution"],
         "answerIndex":1,"explanation":"Fan-out: SNS topic receives one event, fans out to multiple SQS queues, each consumed by different Lambda functions in parallel. Example: OrderPlaced -> simultaneously trigger inventory Lambda, email Lambda, analytics Lambda.","tags":["patterns","fan-out","sns"]},
    ]

    NEW_FC = [
        {"id":"sls-fc4","front":"Lambda cold start mitigation options","back":"1. Provisioned Concurrency (pre-warm containers, costs money)  2. EventBridge keep-alive ping every 5 min (free)  3. Reduce package size (fewer deps, Lambda Layers)  4. Use Python/Node over Java  5. GraalVM native for Java (no JVM startup)","tags":["lambda","cold-start"]},
        {"id":"sls-fc5","front":"Lambda global variable rule","back":"Initialise OUTSIDE handler: DB connections, SDK clients, config (safe, reused across warm invocations = good performance). Store INSIDE handler: per-request user data, request state (not safe to persist across invocations = data leakage).","tags":["lambda","state"]},
        {"id":"sls-fc6","front":"Step Functions when to use","back":"Use when: multi-step workflow with error handling, parallel branches, or human approval. Avoid for: simple A->B Lambda chains that rarely fail. Step Functions cost per state transition — don't overuse for trivial chains.","tags":["step-functions"]},
        {"id":"sls-fc7","front":"Lambda DLQ — why mandatory for async","back":"Async Lambda invocations (SQS, SNS, S3) retry on failure. After retries exhausted, event is LOST unless DLQ configured. DLQ = SQS queue receiving failed events for investigation/replay. Always configure DLQ for async Lambda.","tags":["lambda","dlq","reliability"]},
        {"id":"sls-fc8","front":"Serverless vs container decision","back":"Lambda: sporadic traffic, event-driven, <15min, pay per use, zero ops. ECS/Fargate: long-running, consistent high traffic (cheaper per request at scale), >15min, stateful. EC2: full control, specialised hardware (GPU), legacy apps.","tags":["trade-offs","architecture"]},
    ]

    d['guide'] = GUIDE
    d['questions'] = NEW_Q
    d['flashcards'] = NEW_FC

    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"serverless-patterns.json done: guide={len(GUIDE)} q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ── patch_serverless_fix.py ──────────────────────────────────────────────────────────────────
    p = list(Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics').glob('**/serverless-patterns.json'))[0]
    d = json.loads(p.read_text())

    extra_q = [
        {"id":"sls-q18","type":"mcq","prompt":"What is AWS SAM (Serverless Application Model)?",
         "choices":["A CloudFormation replacement","An AWS framework that extends CloudFormation with serverless-specific resource types (Lambda, API GW, DynamoDB) and provides local testing tools (sam local)",
                    "A Lambda monitoring service","An IAM permission model"],
         "answerIndex":1,"explanation":"SAM simplifies serverless IaC. AWS::Serverless::Function replaces the verbose Lambda + Role + LogGroup resources. sam local invoke and sam local start-api let you test Lambda functions locally before deploying.","tags":["sam","serverless","iac"]},
        {"id":"sls-q19","type":"mcq","prompt":"Why is EventBridge preferred over CloudWatch Events for scheduling Lambda?",
         "choices":["EventBridge is free, CloudWatch Events is paid","EventBridge IS the updated name/service for CloudWatch Events, with added features: schema registry, event buses, archive and replay, richer filtering",
                    "CloudWatch can't schedule Lambda","EventBridge supports more cron formats"],
         "answerIndex":1,"explanation":"Amazon EventBridge was formerly CloudWatch Events — it is the same underlying service, rebranded and extended. EventBridge adds: custom event buses, schema registry, partner event sources, archive and replay. For new projects always use EventBridge naming.","tags":["eventbridge","lambda","scheduling"]},
        {"id":"sls-q20","type":"mcq","prompt":"What is the 'pay per execution' cost model in Lambda?",
         "choices":["Pay $0.20/month per function","Pay for compute time: number of requests x duration in ms x memory GB. First 1 million requests and first 400,000 GB-seconds are FREE every month.",
                    "Pay per deployment","Pay per cold start"],
         "answerIndex":1,"explanation":"Lambda pricing: $0.20 per 1M requests + $0.0000166667 per GB-second. At 512MB and 100ms average: $0.20/M requests + tiny compute. For sporadic workloads this is dramatically cheaper than an EC2 running 24/7. Free tier = 1M req + 400K GB-sec/month forever.","tags":["lambda","pricing","serverless"]},
    ]

    extra_fc = [
        {"id":"sls-fc1-real","front":"Lambda trigger types summary","back":"API Gateway (HTTP request) -> sync response. S3 (file upload) -> async processing. SQS (queue message) -> poll-based batch. EventBridge (schedule/event) -> async. DynamoDB Streams (DB change) -> stream. SNS (notification) -> async fan-out.","tags":["lambda","triggers"]},
        {"id":"sls-fc2-real","front":"Step Functions error handling","back":"Retry: {MaxAttempts:3, IntervalSeconds:2, BackoffRate:2} — exponential backoff. Catch: catch specific error types, transition to error handling state. Much cleaner than try/catch chains inside Lambda code.","tags":["step-functions","error-handling"]},
        {"id":"sls-fc3-real","front":"Serverless cost optimisation tips","back":"1. Right-size memory (profile, don't always use max)  2. Use ARM64 (Graviton) = 20% cheaper + faster  3. Reduce package size (faster cold start = shorter billed duration)  4. Use Lambda SnapStart for Java (cache initialised snapshot)","tags":["lambda","cost"]},
    ]

    existing_qids = {q['id'] for q in d['questions']}
    for q in extra_q:
        if q['id'] not in existing_qids:
            d['questions'].append(q)

    existing_fcids = {fc['id'] for fc in d['flashcards']}
    for fc in extra_fc:
        if fc['id'] not in existing_fcids:
            d['flashcards'].append(fc)

    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"serverless-patterns.json fixed: q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ── patch_sls_final.py ──────────────────────────────────────────────────────────────────
    p = list(Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics').glob('**/serverless-patterns.json'))[0]
    d = json.loads(p.read_text())

    extra = [
        {"id":"sls-q1","type":"mcq","prompt":"What is the cold start problem in AWS Lambda?",
         "choices":["Lambda running out of memory","Lambda function crashing","The latency added when AWS must provision a new container and initialise the runtime for a Lambda function that has been idle","Lambda exceeding its timeout"],
         "answerIndex":2,"explanation":"Cold start = container provisioning overhead. New or idle Lambda containers need JVM/Node/Python startup + code load before handling the request. Java adds 1-3s. Python/Node ~100-300ms.","tags":["lambda","cold-start"]},
        {"id":"sls-q2","type":"mcq","prompt":"Why use Step Functions instead of chaining Lambda A -> Lambda B -> Lambda C in code?",
         "choices":["Step Functions is always faster","Step Functions provides built-in retry/catch/parallel states and visual execution history — direct Lambda chaining has no retry, no audit trail, and nested timeouts are fragile","Step Functions is cheaper","Lambda cannot call other Lambdas"],
         "answerIndex":1,"explanation":"Hand-coded Lambda chains: no built-in retry, cascading timeouts, no execution history. Step Functions manages state machine transitions, retries with exponential backoff, error catching by type, parallel branches, and shows every step in console.","tags":["step-functions","orchestration"]},
        {"id":"sls-q3","type":"mcq","prompt":"Should a Lambda function store temporary per-request user data in a global variable?",
         "choices":["Yes — global variables persist across invocations improving performance","No — Lambda containers are reused: global user data from request A persists into request B on the same warm container, causing data leakage","Yes — Lambda clears globals between invocations","Only for async invocations"],
         "answerIndex":1,"explanation":"Lambda containers are reused for warm invocations. Global variables persist between them. Safe globals: DB connection, SDK client (reusable, not user-specific). Unsafe globals: userId, request data (leaks between users). Keep per-request data inside the handler.","tags":["lambda","state","gotcha"]},
    ]

    existing = {q['id'] for q in d['questions']}
    for q in extra:
        if q['id'] not in existing:
            d['questions'].insert(0, q)

    with open(p, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"serverless-patterns.json: q={len(d['questions'])} fc={len(d['flashcards'])}")

    # ── patch_pycharm.py ──────────────────────────────────────────────────────────────────
    p_py = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/pycharm.json')
    d_py = json.loads(p_py.read_text())

    PYCHARM_GUIDE = "\n".join([
        "# PyCharm Power-Use",
        "",
        "## What Is PyCharm? (Start From Zero)",
        "",
        "PyCharm is an IDE (Integrated Development Environment) built by JetBrains specifically",
        "for Python development. If you have used VS Code, think of PyCharm as a supercharged",
        "version that deeply understands Python — it knows your code structure, catches errors",
        "before you run anything, and automates repetitive tasks.",
        "",
        "**You might ask: why not just use VS Code or Notepad?**",
        "",
        "When you write a single 50-line script, any editor works. But when you work on a",
        "large Python project with hundreds of files, multiple environments, complex dependencies,",
        "and a team of developers — PyCharm's deep tooling saves hours every day.",
        "",
        "```",
        "Editor:                              PyCharm:",
        "  You type code                        Auto-completes as you type",
        "  You run it to find mistakes          Red underlines before you run",
        "  You manually search for a method     Ctrl+click goes to definition instantly",
        "  You read docs in a browser           Docs appear in-editor on hover",
        "  You manually run tests               Run all tests with one click, see results",
        "  You switch Python versions manually  Manage environments in Settings",
        "```",
        "",
        "---",
        "",
        "## Setting Up PyCharm for the First Time",
        "",
        "```",
        "Download: https://www.jetbrains.com/pycharm/",
        "  Community Edition: free, everything covered in this guide",
        "  Professional Edition: paid, adds Django/Flask support, remote dev, DB tools",
        "  Students: free Professional licence via JetBrains Student Pack",
        "",
        "First-time setup checklist:",
        "  1. Open PyCharm, click 'New Project'",
        "  2. Set the project location (folder)",
        "  3. Under Python Interpreter: choose 'New Virtualenv Environment'",
        "     - This creates an isolated Python environment just for this project",
        "     - Libraries installed here don't affect other projects",
        "  4. Click Create",
        "  5. PyCharm creates: your project folder + venv/ subfolder",
        "",
        "Every Python project should have its OWN virtual environment.",
        "Never install everything into the system Python.",
        "```",
        "",
        "---",
        "",
        "## Virtual Environments — Why They Matter",
        "",
        "```",
        "Problem: Project A needs Django 3.2. Project B needs Django 4.2.",
        "Without venv: install both? Python can only have one version installed globally.",
        "Result: one project breaks.",
        "",
        "Solution: Virtual environments",
        "  Project A: venv/ -> Django 3.2, requests 2.28",
        "  Project B: venv/ -> Django 4.2, requests 2.31",
        "  Each project is completely isolated.",
        "",
        "In PyCharm:",
        "  Settings -> Project -> Python Interpreter",
        "  Click gear icon -> Add Interpreter",
        "  Choose: Virtualenv (local), Conda, or system",
        "",
        "From terminal in PyCharm:",
        "  python -m venv venv        # create virtual environment",
        "  source venv/bin/activate   # activate (Mac/Linux)",
        "  venv\\Scripts\\activate    # activate (Windows)",
        "  pip install requests       # installs into THIS venv only",
        "  pip freeze > requirements.txt  # record exact versions",
        "  pip install -r requirements.txt  # recreate on another machine",
        "```",
        "",
        "---",
        "",
        "## The Most Important Keyboard Shortcuts",
        "",
        "Memorising these shortcuts turns PyCharm from a fancy text editor into a superpower.",
        "",
        "```",
        "NAVIGATION (finding things fast):",
        "  Shift+Shift           Search Everywhere — file, class, action, setting",
        "  Ctrl+N  (Cmd+O)       Go to Class by name",
        "  Ctrl+Shift+N          Go to File by name",
        "  Ctrl+Click            Go to Definition — jump to where method/class is defined",
        "  Ctrl+Alt+←/→          Navigate back/forward (like browser history)",
        "  Ctrl+E                Recent files popup",
        "  Alt+F7                Find all usages of selected symbol",
        "  Ctrl+F12              File structure popup — see all methods in current file",
        "",
        "CODE EDITING:",
        "  Ctrl+Space            Code completion",
        "  Ctrl+Shift+Space      Smart completion (context-aware)",
        "  Alt+Enter             Show quick fixes (fix import, create method, suppress warning)",
        "  Ctrl+D                Duplicate line",
        "  Ctrl+Y                Delete line",
        "  Ctrl+/                Comment/uncomment line",
        "  Ctrl+Shift+/          Block comment",
        "  Tab / Shift+Tab       Indent / Unindent selection",
        "  Ctrl+Shift+F          Reformat code (apply PEP 8 style)",
        "  Ctrl+Alt+L  (Cmd+Opt+L)  Reformat file",
        "",
        "REFACTORING:",
        "  Shift+F6              Rename — renames ALL usages simultaneously",
        "  Ctrl+Alt+M            Extract Method — turn selection into a function",
        "  Ctrl+Alt+V            Extract Variable",
        "  Ctrl+Alt+C            Extract Constant",
        "  F6                    Move file/class to different module",
        "",
        "RUNNING & DEBUGGING:",
        "  Shift+F10             Run current configuration",
        "  Shift+F9              Debug current configuration",
        "  Ctrl+F2               Stop running process",
        "  F8                    Step over (debugger)",
        "  F7                    Step into (debugger)",
        "  Shift+F8              Step out (debugger)",
        "  F9                    Resume program (debugger)",
        "",
        "SEARCH:",
        "  Ctrl+F                Find in file",
        "  Ctrl+R                Find and replace in file",
        "  Ctrl+Shift+F          Find in project (all files)",
        "  Ctrl+Shift+R          Replace in project",
        "```",
        "",
        "---",
        "",
        "## Code Completion and Smart Suggestions",
        "",
        "```",
        "Basic completion (Ctrl+Space):",
        "  Type 're' -> PyCharm suggests: requests, re, read, readline...",
        "  Type 'my_list.' -> suggests: append, extend, pop, sort, reverse...",
        "",
        "Smart completion (Ctrl+Shift+Space):",
        "  Knows the TYPE of what you are typing.",
        "  If function expects a str, only shows string variables.",
        "",
        "Postfix completion:",
        "  Type: my_list.for  then press Tab",
        "  Result: for item in my_list:",
        "              ...",
        "",
        "  Type: condition.if  then Tab",
        "  Result: if condition:",
        "              ...",
        "",
        "  Type: 'hello'.len  then Tab",
        "  Result: len('hello')",
        "",
        "Live Templates (code snippets):",
        "  Type 'iter' + Tab -> for item in collection: ...",
        "  Type 'main' + Tab -> if __name__ == '__main__': ...",
        "  Type 'def' + Tab  -> def function_name(params): ...",
        "  Settings -> Editor -> Live Templates to see and add your own",
        "```",
        "",
        "---",
        "",
        "## The Debugger — Step Through Your Code",
        "",
        "The debugger is one of the biggest productivity gains. Instead of adding `print()`",
        "statements everywhere, you pause execution and inspect everything.",
        "",
        "```",
        "HOW TO DEBUG:",
        "  1. Click in the gutter (left margin) next to a line number",
        "     A RED DOT appears — this is a BREAKPOINT",
        "  2. Press Shift+F9 (Debug) instead of Shift+F10 (Run)",
        "  3. Program pauses at the breakpoint",
        "  4. In the Debug panel you see:",
        "     - Variables: current values of ALL variables in scope",
        "     - Call stack: how you got here (which functions called which)",
        "  5. Navigate:",
        "     F8 = Step Over   (go to next line, don't enter calls)",
        "     F7 = Step Into   (go inside the function being called)",
        "     F9 = Resume      (run until next breakpoint)",
        "",
        "EVALUATE EXPRESSION (most powerful feature):",
        "  While paused, press Alt+F8",
        "  Type any Python expression and see its value RIGHT NOW",
        "  e.g.: len(my_list), my_dict.get('key'), type(obj)",
        "  No need to restart or add print statements",
        "",
        "WATCHES:",
        "  In Variables panel, click + to add a watch expression",
        "  PyCharm evaluates it continuously as you step through",
        "",
        "CONDITIONAL BREAKPOINTS:",
        "  Right-click a breakpoint -> Edit",
        "  Add condition: only pause when count > 100",
        "  Useful in loops where you only care about specific iterations",
        "```",
        "",
        "---",
        "",
        "## Integrated Terminal and Run Configurations",
        "",
        "```",
        "TERMINAL (Alt+F12 or View -> Tool Windows -> Terminal):",
        "  Opens a terminal inside PyCharm",
        "  Automatically activates your project's virtualenv",
        "  Run: pip install, git commands, scripts",
        "",
        "RUN CONFIGURATIONS:",
        "  A saved set of 'how to run this program'",
        "  Top right dropdown -> Edit Configurations",
        "",
        "  Add configuration:",
        "    Script path: path to your main.py",
        "    Parameters: command-line arguments",
        "    Environment variables: DB_URL=..., DEBUG=True",
        "    Working directory: where to run from",
        "",
        "  Why save configurations?",
        "  - Run the same script with one button",
        "  - Different configs for dev/test/prod",
        "  - Set env vars without modifying code",
        "  - Share via .run/ folder in git (optional)",
        "```",
        "",
        "---",
        "",
        "## Refactoring Tools",
        "",
        "```",
        "RENAME (Shift+F6) — the most-used refactoring:",
        "  Place cursor on variable/function/class name",
        "  Press Shift+F6",
        "  Type new name -> Enter",
        "  PyCharm renames EVERY occurrence in the ENTIRE project",
        "  Including string references and comments (optional)",
        "  This is safe: PyCharm understands the code, not just text",
        "",
        "EXTRACT METHOD (Ctrl+Alt+M):",
        "  Select a block of code",
        "  Press Ctrl+Alt+M",
        "  Name the new function",
        "  PyCharm creates the function, moves the code, adds the call",
        "  Parameters are inferred from used variables",
        "",
        "EXTRACT VARIABLE (Ctrl+Alt+V):",
        "  Select an expression: len(my_list) * 2",
        "  Press Ctrl+Alt+V",
        "  Name it: doubled_length",
        "  Code becomes: doubled_length = len(my_list) * 2",
        "  All occurrences of that expression are replaced",
        "",
        "MOVE (F6):",
        "  Move a class/function to a different file/module",
        "  All imports are updated automatically",
        "```",
        "",
        "---",
        "",
        "## Code Inspections and Quick Fixes",
        "",
        "```",
        "PyCharm continuously analyses your code and shows problems:",
        "",
        "Red underline:     Error — code will not run (undefined name, syntax error)",
        "Yellow underline:  Warning — potential issue (unused import, shadowed variable)",
        "Green underline:   Weak warning — style suggestion",
        "",
        "Quick Fix (Alt+Enter on any underlined code):",
        "  Missing import -> 'Import requests'",
        "  Undefined method -> 'Create method'",
        "  Wrong type -> type annotation suggestion",
        "  Long line -> 'Split string'",
        "  Unused variable -> 'Rename to _'",
        "",
        "The inspection marker in the top-right gutter shows overall file health.",
        "Green check = no issues. Yellow = warnings. Red = errors.",
        "",
        "Run inspections on whole project:",
        "  Analyze -> Inspect Code",
        "  See all issues across ALL files at once",
        "```",
        "",
        "---",
        "",
        "## Testing with PyTest in PyCharm",
        "",
        "```",
        "SETUP:",
        "  Settings -> Tools -> Python Integrated Tools",
        "  Default test runner: pytest",
        "",
        "RUNNING TESTS:",
        "  Green run icon next to test function/class/file",
        "  Click to run that specific test",
        "  Ctrl+Shift+F10 = run tests in current file",
        "  Run -> Run All Tests = run entire test suite",
        "",
        "TEST PANEL:",
        "  Shows all tests: green = passed, red = failed",
        "  Click a failed test to see the assertion error",
        "  Re-run only failed tests (useful for large suites)",
        "",
        "DEBUGGING A TEST:",
        "  Click the debug icon (bug icon) next to a test",
        "  Set a breakpoint in your test or the tested code",
        "  Step through to see exactly why it fails",
        "",
        "COVERAGE:",
        "  Run with Coverage (Shift+Alt+F10, or right-click -> Run with Coverage)",
        "  Editor shows: green lines = covered, red = not covered by tests",
        "  Highlights exactly which code paths your tests miss",
        "```",
        "",
        "---",
        "",
        "## Git Integration",
        "",
        "```",
        "PyCharm has full Git support without leaving the IDE.",
        "",
        "COMMIT (Ctrl+K):",
        "  Opens commit panel",
        "  See all changed files (diff on right)",
        "  Check which files to include",
        "  Write commit message",
        "  Press Commit (or Commit and Push)",
        "",
        "PUSH (Ctrl+Shift+K):",
        "  Push committed changes to remote",
        "",
        "PULL:",
        "  Git menu -> Pull (or fetch first to see what's incoming)",
        "",
        "DIFF VIEW:",
        "  Right-click any file -> Git -> Compare with Branch",
        "  Side-by-side diff of your changes vs any branch",
        "",
        "HISTORY (RIGHT-CLICK FILE):",
        "  Show History -> see every commit that touched this file",
        "  Who changed it, when, what was the message",
        "  Click any revision to see the diff",
        "",
        "ANNOTATE (git blame):",
        "  Right-click in editor gutter -> Annotate with Git Blame",
        "  Each line shows: author, date, commit hash",
        "",
        "RESOLVE MERGE CONFLICTS:",
        "  PyCharm shows a 3-panel merge tool",
        "  Left: your changes, Middle: result, Right: incoming",
        "  Click arrows to accept/reject each change",
        "  Much cleaner than resolving conflicts in a terminal",
        "```",
        "",
        "---",
        "",
        "## Database Tools (Professional Edition)",
        "",
        "```",
        "View -> Tool Windows -> Database",
        "  Add Data Source: PostgreSQL, MySQL, SQLite, etc.",
        "  Enter connection details",
        "",
        "Once connected:",
        "  Browse tables in tree view",
        "  Run SQL queries in an editor with autocomplete",
        "  Edit cells directly in the table view",
        "  Export query results as CSV",
        "  View table structure (columns, types, indexes)",
        "",
        "SQL autocomplete:",
        "  PyCharm knows your schema",
        "  SELECT * FROM  ->  suggests table names",
        "  WHERE user.  ->  suggests column names",
        "  Joins are autocompleted based on foreign keys",
        "```",
        "",
        "---",
        "",
        "## Mind Map",
        "",
        "```",
        "PYCHARM POWER-USE",
        "|",
        "+-- ENVIRONMENTS",
        "|   +-- Virtual environments (isolated per project)",
        "|   +-- Settings -> Python Interpreter",
        "|   +-- pip + requirements.txt",
        "|",
        "+-- NAVIGATION",
        "|   +-- Shift+Shift (search everywhere)",
        "|   +-- Ctrl+Click (go to definition)",
        "|   +-- Alt+F7 (find usages)",
        "|   +-- Ctrl+E (recent files)",
        "|",
        "+-- EDITING",
        "|   +-- Alt+Enter (quick fixes)",
        "|   +-- Shift+F6 (rename all usages)",
        "|   +-- Ctrl+Alt+M (extract method)",
        "|   +-- Ctrl+Alt+L (reformat code)",
        "|",
        "+-- DEBUGGING",
        "|   +-- Breakpoints (click gutter)",
        "|   +-- Step Over/Into/Out (F8/F7/Shift+F8)",
        "|   +-- Evaluate Expression (Alt+F8)",
        "|   +-- Conditional breakpoints",
        "|",
        "+-- TESTING",
        "|   +-- Run/debug individual tests",
        "|   +-- Coverage view",
        "|   +-- Re-run failed only",
        "|",
        "+-- GIT",
        "|   +-- Commit (Ctrl+K)",
        "|   +-- History / Blame",
        "|   +-- Merge conflict tool",
        "|",
        "+-- RUN CONFIGS",
        "    +-- Script path + args + env vars",
        "    +-- Multiple configs per project",
        "```",
        "",
        "---",
        "",
        "## References and Further Learning",
        "",
        "### Videos (Watch These!)",
        "- **PyCharm Tips and Tricks** by JetBrains (official):",
        "  https://www.youtube.com/watch?v=NoDx0MEESDw",
        "  - Official JetBrains video. Demonstrates key features in real workflow.",
        "- **Top 10 PyCharm Shortcuts You Need to Know** by Tech With Tim:",
        "  https://www.youtube.com/watch?v=Gz0f8iFhOAs",
        "  - Practical shortcuts with demos. Great for beginners.",
        "",
        "### Free Books and Articles",
        "- **PyCharm official documentation**: https://www.jetbrains.com/help/pycharm/",
        "  - 'Getting Started' and 'Debugging' sections are most useful first.",
        "- **JetBrains Academy** (interactive Python + PyCharm course): https://hyperskill.org/",
        "  - Free tier available. Learn Python while using PyCharm features.",
        "",
        "### Diagrams and Cheatsheets",
        "- **PyCharm Keyboard Shortcuts PDF (Mac)**: https://resources.jetbrains.com/storage/products/pycharm/docs/PyCharm_ReferenceCard_mac.pdf",
        "- **PyCharm Keyboard Shortcuts PDF (Win/Linux)**: https://resources.jetbrains.com/storage/products/pycharm/docs/PyCharm_ReferenceCard.pdf",
        "  - Print this and stick it on your monitor. Use it daily for 2 weeks — muscle memory locks in.",
        "",
        "### Practice",
        "- **JetBrains IDE Features Trainer** (built into PyCharm!):",
        "  Help -> IDE Features Trainer",
        "  Built-in interactive lessons for shortcuts and features. Do all of them.",
    ])

    PYCHARM_NEW_Q = [
        {"id":"pycharm-q1-real","type":"mcq","prompt":"What is the keyboard shortcut to search for ANYTHING in PyCharm (files, classes, actions, settings)?",
         "choices":["Ctrl+F","Ctrl+N","Shift+Shift (double Shift)","Ctrl+Shift+F"],
         "answerIndex":2,"explanation":"Double Shift opens 'Search Everywhere' — a single dialog that finds files, classes, symbols, actions, and settings. The single most useful shortcut in PyCharm.","tags":["shortcuts","navigation"]},
        {"id":"pycharm-q2-real","type":"mcq","prompt":"What does Alt+Enter do in PyCharm?",
         "choices":["Runs the current file","Opens terminal","Shows context-aware quick fixes — adds missing imports, creates missing methods, fixes type issues",
                    "Formats the code"],
         "answerIndex":2,"explanation":"Alt+Enter is PyCharm's magic wand. On any red/yellow underline, it offers intelligent fixes. Most common: auto-import a missing module. Learn this one shortcut and your productivity triples immediately.","tags":["shortcuts","quick-fixes"]},
        {"id":"pycharm-q3-real","type":"mcq","prompt":"Why should each Python project have its own virtual environment?",
         "choices":["Virtual environments make code run faster","They allow different projects to have different (potentially conflicting) dependency versions without interfering with each other","They are required by PyCharm","They encrypt your code"],
         "answerIndex":1,"explanation":"Project A needs Django 3.2, Project B needs Django 4.2. Without venv, only one can be installed globally. Virtual environments give each project an isolated Python environment with its own packages.","tags":["virtualenv","environments"]},
        {"id":"pycharm-q4-real","type":"mcq","prompt":"You want to rename a function used in 50 files. What is the safest way in PyCharm?",
         "choices":["Find+Replace in all files","Manually edit each file","Shift+F6 (Rename refactoring) — PyCharm finds and renames ALL usages across the entire project safely",
                    "Delete and rewrite"],
         "answerIndex":2,"explanation":"Rename refactoring (Shift+F6) understands code structure — not just text. It renames the definition and every reference. Find+Replace is text-based and can rename unrelated things with the same name.","tags":["refactoring","rename"]},
        {"id":"pycharm-q5-real","type":"mcq","prompt":"What does Ctrl+Click on a function name do?",
         "choices":["Runs the function","Copies the function","Jumps to the function's definition — wherever it is defined in the codebase",
                    "Deletes the function"],
         "answerIndex":2,"explanation":"Go to Definition instantly navigates you to where the function/class/variable was defined — in the same file, another file, or even inside a library. Essential for understanding unfamiliar codebases.","tags":["navigation","shortcuts"]},
        {"id":"pycharm-q6-real","type":"mcq","prompt":"You set a breakpoint and press Shift+F9. Execution pauses. You press F8. What happens?",
         "choices":["Program terminates","Execution jumps to the next breakpoint","Executes the current line and moves to the next line WITHOUT entering any called functions (Step Over)",
                    "Enters the function on the current line"],
         "answerIndex":2,"explanation":"F8 = Step Over. Runs the current line and stops at the next. If the line calls a function, that function runs entirely — you stay at the same level. F7 = Step Into (enters the function call).","tags":["debugging","shortcuts"]},
        {"id":"pycharm-q7-real","type":"mcq","prompt":"What is the Evaluate Expression feature in the debugger?",
         "choices":["Runs the entire program","Evaluates a Python expression in the current paused stack frame — lets you inspect any value or test any code without restarting",
                    "Shows stack trace","Opens the terminal"],
         "answerIndex":1,"explanation":"While paused at a breakpoint (Alt+F8): type any Python expression and see its value right now. type(my_var), len(list), my_dict['key'] — all evaluated in the CURRENT execution context. Huge time saver.","tags":["debugging","evaluate"]},
        {"id":"pycharm-q8-real","type":"mcq","prompt":"What does Ctrl+Alt+M (Extract Method) do?",
         "choices":["Creates a new method from scratch","Moves the selected code block into a new function, with parameters inferred from used variables, and replaces the selection with a call to that function",
                    "Copies a method","Deletes a method"],
         "answerIndex":1,"explanation":"Extract Method is one of the most powerful refactorings. Select any block of code, press Ctrl+Alt+M, name the function — PyCharm moves the code, figures out what parameters are needed, and inserts the function call.","tags":["refactoring","extract"]},
        {"id":"pycharm-q9-real","type":"mcq","prompt":"What does 'Run with Coverage' show in PyCharm?",
         "choices":["Performance profiling data","Memory usage","Green/red highlighting in the editor showing which lines ARE covered by tests and which are NOT",
                    "Security vulnerabilities"],
         "answerIndex":2,"explanation":"Coverage runs your tests and marks each line: green = executed by some test, red = never executed. You can visually see which code paths your tests miss — making it obvious where to add test cases.","tags":["testing","coverage"]},
        {"id":"pycharm-q10-real","type":"mcq","prompt":"What is a Run Configuration in PyCharm?",
         "choices":["A Python configuration file","A saved setup for running a script — script path, arguments, environment variables, working directory — so you can run it consistently with one click",
                    "A virtualenv setting","A test framework"],
         "answerIndex":1,"explanation":"Run Configurations save how to run your program: which script, with what args, with which env vars. Multiple configs per project: 'Run dev server', 'Run tests', 'Run migration'. Never type long commands again.","tags":["run-config","productivity"]},
        {"id":"pycharm-q11-real","type":"mcq","prompt":"What does Shift+F6 do in PyCharm?",
         "choices":["Formats code","Renames the symbol under cursor and ALL its usages across the entire project simultaneously",
                    "Runs tests","Opens settings"],
         "answerIndex":1,"explanation":"Rename refactoring. The most important refactoring. Cursor on a variable, function, class, or file name -> Shift+F6 -> type new name -> Enter. Every reference is updated. Safe, complete, instant.","tags":["refactoring","shortcuts"]},
        {"id":"pycharm-q12-real","type":"mcq","prompt":"What information does the PyCharm debugger's Variables panel show while paused at a breakpoint?",
         "choices":["Stack trace only","Current values of all variables in scope at the breakpoint — their names, types, and values",
                    "Error messages","Code coverage"],
         "answerIndex":1,"explanation":"The Variables panel shows every variable in the current scope: local variables, parameters, self attributes. Click to expand objects and see their internals. No print() needed.","tags":["debugging","variables"]},
        {"id":"pycharm-q13-real","type":"mcq","prompt":"In PyCharm's Git integration, what does Ctrl+K open?",
         "choices":["Push dialog","Pull dialog","Commit dialog — shows changed files, diff preview, commit message field",
                    "Branch manager"],
         "answerIndex":2,"explanation":"Ctrl+K opens the Commit panel. See all modified files, review diffs side-by-side, write your commit message, choose which files to include — all without leaving PyCharm.","tags":["git","shortcuts"]},
        {"id":"pycharm-q14-real","type":"mcq","prompt":"What does a red underline in PyCharm code mean?",
         "choices":["Code style suggestion","A warning about a potential issue","An error — the code will not run: undefined name, syntax error, wrong argument count",
                    "A comment"],
         "answerIndex":2,"explanation":"Red = error. PyCharm's static analysis catches real bugs: undefined variables, wrong number of arguments, imported but missing modules. Fix these before running — they are always real problems.","tags":["inspections","errors"]},
        {"id":"pycharm-q15-real","type":"mcq","prompt":"How do you search for a method/class name across ALL files in the project?",
         "choices":["Ctrl+F (in current file only)","Ctrl+Shift+F (Find in Path — searches all files in project)",
                    "Ctrl+N","Alt+F7"],
         "answerIndex":1,"explanation":"Ctrl+Shift+F opens Find in Path — searches all project files for text. Add file type filter (*.py) and case sensitivity. Alt+F7 finds usages of a specific symbol (smarter than text search).","tags":["search","navigation"]},
        {"id":"pycharm-q16-real","type":"mcq","prompt":"What is a conditional breakpoint and when would you use one?",
         "choices":["A breakpoint in an if statement","A breakpoint that only pauses execution when a specified condition is true — useful when a bug only occurs for certain values in a loop",
                    "A breakpoint that logs to console","A disabled breakpoint"],
         "answerIndex":1,"explanation":"Right-click a breakpoint -> Edit, add condition e.g. i == 999. Without conditional breakpoints, you would press F9 999 times to reach the interesting iteration. Conditional breakpoints go straight to the relevant case.","tags":["debugging","breakpoints"]},
        {"id":"pycharm-q17-real","type":"mcq","prompt":"What does `pip freeze > requirements.txt` do and why is it important?",
         "choices":["Installs packages","Clears the virtual environment","Records the exact version of every installed package to a text file — allows exact environment recreation on any machine",
                    "Updates all packages"],
         "answerIndex":2,"explanation":"requirements.txt lists exact versions: requests==2.31.0, Django==4.2.1. Anyone can run pip install -r requirements.txt and get the identical environment. Essential for reproducible deployments and team collaboration.","tags":["virtualenv","dependencies"]},
        {"id":"pycharm-q18-real","type":"mcq","prompt":"When PyCharm shows 'Annotate with Git Blame' in the editor gutter, what does it display?",
         "choices":["Test coverage","Memory usage per line","For each line: who last modified it, when, and in which commit",
                    "Code complexity"],
         "answerIndex":2,"explanation":"Git Blame annotation shows the author, date, and commit hash next to each line. Invaluable for understanding why code was written a certain way, who to ask about it, and when a bug was introduced.","tags":["git","blame"]},
        {"id":"pycharm-q19-real","type":"mcq","prompt":"What is the IDE Features Trainer in PyCharm?",
         "choices":["A plugin for training ML models","A built-in interactive tutorial that teaches PyCharm features through hands-on lessons inside the IDE itself",
                    "A performance profiler","A code review tool"],
         "answerIndex":1,"explanation":"Help -> IDE Features Trainer. Interactive lessons that walk you through shortcuts and features directly in the editor. Better than reading docs — you practice each feature immediately in context.","tags":["learning","shortcuts"]},
        {"id":"pycharm-q20-real","type":"mcq","prompt":"What is the key benefit of PyCharm's 'Extract Variable' refactoring (Ctrl+Alt+V)?",
         "choices":["Speeds up execution","Gives a complex expression a meaningful name as a variable — improving readability and replacing all occurrences of that expression simultaneously",
                    "Moves code to another file","Adds type annotations"],
         "answerIndex":1,"explanation":"Select: len(items) * price_per_unit. Extract Variable. Name it: total_cost. Now every place that expression appeared is replaced with total_cost. Code becomes self-documenting.","tags":["refactoring","readability"]},
    ]

    PYCHARM_NEW_FC = [
        {"id":"pycharm-fc1-real","front":"Top 5 PyCharm shortcuts to learn first","back":"1. Shift+Shift (search everywhere)  2. Alt+Enter (quick fix)  3. Ctrl+Click (go to definition)  4. Shift+F6 (rename all)  5. Ctrl+Alt+L (reformat code). Master these five, learn the rest gradually.","tags":["shortcuts"]},
        {"id":"pycharm-fc2-real","front":"Debugger: F7 vs F8 vs F9","back":"F8=Step Over (run line, don't enter calls)  F7=Step Into (enter the function being called)  Shift+F8=Step Out (finish current function, return to caller)  F9=Resume (run to next breakpoint)","tags":["debugging"]},
        {"id":"pycharm-fc3-real","front":"Alt+Enter — when to use it","back":"On ANY red/yellow underline. Common fixes: add missing import, create missing method/variable, change to compatible type, suppress warning, split long string. The single most important shortcut for fixing problems fast.","tags":["quick-fixes","shortcuts"]},
        {"id":"pycharm-fc4-real","front":"Virtual environment best practices","back":"One venv per project. Never use system Python for projects. Always pip freeze > requirements.txt after installing. Commit requirements.txt to git (not the venv/ folder itself — add venv/ to .gitignore).","tags":["virtualenv","environments"]},
        {"id":"pycharm-fc5-real","front":"Rename refactoring vs Find+Replace","back":"Shift+F6 (Rename): understands code structure, renames only the correct symbol across all files. Find+Replace: text-based, may rename unrelated things with same name. Always use Rename for code symbols.","tags":["refactoring"]},
        {"id":"pycharm-fc6-real","front":"Run Configuration use cases","back":"Save: script path, CLI args, env vars (DB_URL=..., DEBUG=True), working directory. Multiple configs: 'Run dev', 'Run tests', 'Run migrations'. Eliminates typing long commands. Share via .run/ in git.","tags":["run-config","productivity"]},
        {"id":"pycharm-fc7-real","front":"Code coverage workflow","back":"Run with Coverage -> editor shows green (covered) and red (not covered) lines. Red lines = your tests never execute that code path. Add test cases targeting red paths until all critical code is green.","tags":["testing","coverage"]},
        {"id":"pycharm-fc8-real","front":"Evaluate Expression during debugging","back":"Alt+F8 while paused at breakpoint. Type any Python expression: len(items), type(x), my_obj.attr. Evaluated in CURRENT execution context. Test hypotheses about bugs without adding print statements or restarting.","tags":["debugging","evaluate"]},
    ]

    # Replace ALL questions and flashcards (existing ones are garbage stubs)
    d_py['guide'] = PYCHARM_GUIDE
    d_py['questions'] = PYCHARM_NEW_Q
    d_py['flashcards'] = PYCHARM_NEW_FC

    with open(p_py, 'w') as f:
        json.dump(d_py, f, indent=2, ensure_ascii=False)
    print(f"pycharm.json done: guide={len(PYCHARM_GUIDE)} q={len(d_py['questions'])} fc={len(d_py['flashcards'])}")

if __name__ == '__main__':
    main()
