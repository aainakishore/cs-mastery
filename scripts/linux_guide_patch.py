import json
from pathlib import Path

p = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/cloud-devops/linux-essentials.json')
d = json.loads(p.read_text())

NEW_GUIDE = r"""# Linux Essentials

## What Even Is Linux? (Start Here If You're New)

Imagine your computer is a restaurant. The **hardware** (CPU, RAM, disk) is the kitchen equipment. The **operating system** is the head chef who controls everything — decides who gets to use the grills, hands out ingredients, and keeps order. Linux is one such head chef, and it runs on almost every server, cloud machine, Docker container, and CI/CD pipeline in the world.

You've likely used Windows or macOS as your personal computer OS. Linux is different — it was designed from the ground up for servers, automation, and multi-user environments. It's fast, stable, free, and open source (anyone can read or modify its code).

**Why should a developer learn Linux?**
- Your code runs on Linux servers (AWS EC2, GCP, Azure — all Linux under the hood)
- Docker containers are Linux
- CI/CD pipelines run bash scripts on Linux
- SSH into any production machine = you're in a Linux terminal
- Kubernetes pods run Linux containers

```
Your laptop (macOS/Windows)
        |
        | SSH connection
        ↓
Linux Server (AWS EC2, GCP VM, your VPS...)
  - Ubuntu 22.04 LTS
  - CentOS / RHEL
  - Debian
  - Alpine (used inside Docker)
```

---

## The Terminal — Your New Best Friend

When you work with Linux, you don't click around a graphical UI. You type commands in a **terminal** (also called shell, command line, or CLI — Command Line Interface).

**Analogy:** Think of the terminal like texting your computer. Instead of clicking "New Folder", you type `mkdir my-folder`. It's faster once you learn the language.

The most common shell is **bash** (Bourne Again Shell). When you open a terminal, you see a prompt like:

```
alice@myserver:~$
  │       │    │ └─ $ means you're a regular user (# means root/admin)
  │       │    └─── ~ means you're in your home directory
  │       └──────── hostname (server name)
  └──────────────── your username
```

You type a command and press Enter. The shell executes it and shows output. That's it.

```
alice@myserver:~$ echo "Hello Linux"
Hello Linux
alice@myserver:~$          ← prompt returns, ready for next command
```

---

## The Filesystem — Everything Is a File

Linux has one giant directory tree. Everything lives inside it — programs, configs, logs, even hardware devices (yes, hardware!).

```
/                          ← the "root" — the very top of everything
├── bin/                   ← essential programs: ls, cp, mv, echo
├── sbin/                  ← system admin programs: fdisk, ip, reboot
├── etc/                   ← ALL configuration files live here
│   ├── nginx/
│   │   └── nginx.conf     ← Nginx web server config
│   ├── ssh/
│   │   └── sshd_config    ← SSH server settings
│   └── hosts              ← hostname → IP mappings
├── home/                  ← user home directories
│   ├── alice/             ← alice's personal space (~)
│   └── bob/
├── var/                   ← variable data that changes over time
│   └── log/               ← LOG FILES live here!
│       ├── syslog         ← system-wide events
│       ├── auth.log       ← login attempts
│       └── nginx/
│           └── access.log ← every HTTP request
├── tmp/                   ← temporary files — WIPED on reboot
├── usr/                   ← user-installed programs and libraries
│   ├── bin/               ← programs installed by apt/yum
│   └── lib/               ← shared libraries (.so files)
├── proc/                  ← VIRTUAL filesystem — shows running processes
│   ├── 1234/              ← folder named after PID (process ID)
│   │   └── status         ← read this file to see process info
│   └── cpuinfo            ← CPU info (try: cat /proc/cpuinfo)
└── dev/                   ← device files (disks, terminals, etc.)
    ├── sda                ← your primary hard drive
    └── tty1               ← terminal device
```

**Analogy:** Think of `/` like the root of a company building:
- `/etc` = the HR / Policy office (all the rules and configs)
- `/var/log` = the security camera footage room (audit logs)
- `/home/alice` = Alice's personal office
- `/tmp` = a whiteboard that gets erased every morning
- `/usr/bin` = where all the software tools are stored

**Real-world scenario:** Your Java Spring Boot app crashes at 3am. You SSH in and:
1. Go to `/var/log/` to find your app's log file
2. Run `tail -100 /var/log/myapp/app.log` to see the last 100 lines
3. Spot the `OutOfMemoryError`, understand it, fix the heap setting in config

---

## Navigating the Filesystem

These are the commands you'll use constantly:

```bash
# WHERE AM I?
pwd
# Output: /home/alice
# pwd = Print Working Directory — your current location

# WHAT'S IN HERE?
ls              # list files
ls -l           # long format (permissions, size, date)
ls -a           # include hidden files (starting with .)
ls -lah         # l=long, a=all, h=human-readable sizes
# Output example:
# drwxr-xr-x  3 alice alice 4.0K Jan 15 09:00 projects/
# -rw-r--r--  1 alice alice  82K Jan 14 18:30 notes.txt

# MOVE AROUND
cd /etc                # go to /etc (absolute path)
cd projects            # go to projects/ (relative path)
cd ..                  # go up one level
cd ~                   # go to your home directory
cd -                   # go back to where you just were (like "back" button)

# CREATE THINGS
mkdir photos           # make a directory
mkdir -p a/b/c/d       # make nested directories (creates all at once)
touch notes.txt        # create empty file (or update its timestamp)

# COPY, MOVE, DELETE
cp file.txt backup.txt        # copy a file
cp -r folder/ backup_folder/  # copy a folder (recursive)
mv old_name.txt new_name.txt  # rename or move
mv file.txt /tmp/             # move to /tmp
rm file.txt                   # delete a file (NO RECYCLE BIN!)
rm -rf folder/                # delete folder and everything inside (CAREFUL!)
```

> ⚠️ **WARNING:** `rm -rf` has no undo. There is no recycle bin. If you delete something, it's gone. Always double-check before running `rm -rf`.

---

## Reading Files

```bash
cat file.txt          # print entire file to screen
less file.txt         # page through a large file (q to quit, / to search)
head -20 file.txt     # show first 20 lines
tail -20 file.txt     # show last 20 lines
tail -f app.log       # LIVE follow — shows new lines as they're written
                      # Perfect for watching logs in real time!

# Search inside files
grep "ERROR" app.log                    # find lines with "ERROR"
grep -i "error" app.log                 # case-insensitive
grep -r "database" /etc/               # search recursively in all files
grep -n "NullPointerException" app.log  # show line numbers
```

**Real-world scenario:** App is throwing errors in production. You run:
```bash
tail -f /var/log/myapp/app.log | grep ERROR
```
This shows only ERROR lines as they happen, live. You can see exactly what's failing.

---

## File Permissions — Who Can Do What

Every file in Linux has three sets of permissions for three groups of people:

```
-rw-r--r--  1  alice  developers  4096  Jan 15  report.txt
│          │   │      │
│          │   │      └─ group name
│          │   └──────── owner name
│          └──────────── number of hard links
└─────────────────────── permission string (10 characters)
```

**Breaking down the permission string:**
```
- r w - r - - r - -
│ │ │ │ │ │ │ │ │ │
│ └─┬─┘ └─┬─┘ └─┬─┘
│  owner  group others
│
└─ file type: - = regular file, d = directory, l = symlink
```

**r, w, x meaning:**
```
r = read    = can you open/read the file? (value: 4)
w = write   = can you edit/delete the file? (value: 2)
x = execute = can you run it as a program? (value: 1)
- = no permission for that slot
```

**The numbers in chmod:**
```
rwx = 4+2+1 = 7   (full access)
rw- = 4+2+0 = 6   (read + write)
r-x = 4+0+1 = 5   (read + execute)
r-- = 4+0+0 = 4   (read only)
--- = 0+0+0 = 0   (no access)

chmod 755 script.sh
       │││
       ││└── others: 5 = r-x (can read and run, can't write)
       │└─── group:  5 = r-x
       └──── owner:  7 = rwx (full access)

chmod 600 private_key
       │││
       ││└── others: 0 = --- (no access at all)
       │└─── group:  0 = --- (no access at all)
       └──── owner:  6 = rw- (can read and write)
```

**Common permission recipes:**
```bash
chmod 755 script.sh      # Shell scripts: owner full, everyone can read/run
chmod 644 config.txt     # Config files: owner can edit, everyone can read
chmod 600 ~/.ssh/id_rsa  # SSH private key: ONLY owner can read (SSH requires this!)
chmod +x deploy.sh       # Just add execute bit without changing others
chmod -R 755 /var/www/   # Recursive: apply to all files in folder
```

**chown — change who owns a file:**
```bash
chown alice report.txt              # change owner to alice
chown alice:developers report.txt   # change owner AND group
sudo chown -R www-data /var/www/html  # change owner recursively
```

**Real-world pitfall:** Your app can't write its log files. You check:
```bash
ls -la /var/log/
# drwxr-xr-x  2  root  root  4096  ...  myapp/
# The folder is owned by root! Your app user can't write.
```
Fix: `sudo chown -R myappuser:myappuser /var/log/myapp/`

---

## Processes — Running Programs

When you run a program, the OS creates a **process** — an instance of the program with its own memory, files, and a unique **PID** (Process ID).

```
You type: java -jar app.jar
                │
                ↓
Kernel allocates:
  PID: 4521
  Memory: 512MB heap
  Files: opens app.jar, log file, network sockets
  CPU time: gets scheduled on available core
                │
                ↓
Process runs until:
  - Normal exit (System.exit(0))
  - Error crash
  - You kill it (SIGTERM or SIGKILL)
```

**Key process commands:**
```bash
ps aux
# Shows ALL running processes
# a = all users, u = user-oriented format, x = include background
# Output:
# USER   PID  %CPU  %MEM  COMMAND
# alice  4521  25.3  12.8  java -jar app.jar
# root    234   0.1   0.2  nginx: master process

top           # live updating process viewer (like Task Manager)
htop          # prettier version of top (may need: sudo apt install htop)
              # Press q to quit

pgrep nginx   # find PID of process named "nginx"
pgrep -a java # find all java processes with their full command

# STOPPING PROCESSES
kill 4521       # send SIGTERM (15) — politely ask process to stop
kill -9 4521    # send SIGKILL — force kill immediately (no cleanup chance!)
killall java    # kill all processes named "java"

# Why use SIGTERM first?
# SIGTERM lets the app: close DB connections, flush logs, finish current request
# SIGKILL immediately terminates — like pulling the power cable
```

**Background processes:**
```bash
./long_script.sh &         # & = run in background immediately
                           # You get your prompt back right away

nohup ./server.sh &        # nohup = don't stop when terminal closes
                           # useful for long-running tasks

jobs                       # list background jobs in current terminal
fg %1                      # bring job #1 to foreground
bg %1                      # resume suspended job in background

Ctrl+Z                     # suspend (pause) current foreground process
Ctrl+C                     # interrupt (stop) current foreground process
```

---

## Pipes and Redirection — Combining Commands

This is where Linux gets really powerful. You can **chain commands together** so the output of one becomes the input of the next.

**The pipe `|` operator:**
```
command1 | command2 | command3
    │           │           │
    │      takes output     │
    │      of command1      │
    │      as its input     └── takes output of command2 as input
    └── runs first
```

**Real examples:**
```bash
# Find top 10 IPs making requests to your server
cat access.log | grep 'POST' | awk '{print $1}' | sort | uniq -c | sort -rn | head -10
#      │               │             │              │        │            │         │
#      │          filter POSTs       │           alphabetical  count     sort by   first 10
#      read file                  extract         sort      duplicates  count (desc)
#                                  1st column

# Count how many ERROR lines in a log
grep 'ERROR' app.log | wc -l

# Find all Java processes and show only PIDs
ps aux | grep java | awk '{print $2}'
```

**Redirection — sending output to files:**
```bash
ls -la > filelist.txt        # > OVERWRITES the file (creates if not exists)
ls -la >> filelist.txt       # >> APPENDS to the file
cat nonexistent 2> errors.txt  # 2> redirects stderr (error output)
java -jar app.jar > app.log 2>&1  # redirect BOTH stdout and stderr to same file
                              # 2>&1 means "send file descriptor 2 to where 1 goes"

# Run in background AND redirect output:
nohup java -jar app.jar > app.log 2>&1 &
```

**Analogy:** Pipes are like an assembly line in a factory. Each worker specialist does exactly one job, takes input from the previous conveyor belt, transforms it, and passes it on. No worker knows (or cares) what comes before or after them.

---

## Finding Things

```bash
# find - search by file metadata
find /var/log -name "*.log"              # all .log files under /var/log
find /home -name "*.txt" -user alice     # text files owned by alice
find /tmp -mtime +7                      # files not modified in 7+ days
find . -size +100M                       # files over 100MB in current dir
find /etc -type f -name "*.conf"         # only files (not dirs) matching *.conf

# grep - search file CONTENTS
grep "NullPointerException" app.log      # lines containing this text
grep -i "error" app.log                  # case insensitive
grep -r "database_url" /etc/             # search all files recursively
grep -l "TODO" *.java                    # just show filenames that match
grep -c "ERROR" app.log                  # count of matching lines
grep -A 3 -B 3 "FATAL" app.log          # show 3 lines before and after each match

# which - find where a program is installed
which java      # → /usr/bin/java
which nginx     # → /usr/sbin/nginx

# locate - fast filename search (uses a pre-built index)
locate nginx.conf   # finds all files named nginx.conf instantly
sudo updatedb       # update the index (run if locate is outdated)
```

---

## Environment Variables and the PATH

Environment variables are **key=value settings** that programs can read. They're how you configure programs without editing code.

```bash
# View all environment variables
env

# View a specific one
echo $HOME      # → /home/alice
echo $USER      # → alice
echo $PATH      # → /usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

# Set a variable (only lasts for this terminal session)
export MY_DB_URL="postgresql://localhost:5432/mydb"

# Set permanently (add to ~/.bashrc or ~/.bash_profile)
echo 'export MY_DB_URL="postgresql://localhost:5432/mydb"' >> ~/.bashrc
source ~/.bashrc   # reload the file so it takes effect NOW
```

**PATH explained:**
```
PATH=/usr/local/bin:/usr/bin:/bin
           │             │      │
           │             │      └── check /bin/ for the command
           │             └───────── check /usr/bin/ for the command
           └─────────────────────── check /usr/local/bin/ FIRST

When you type: java
Linux looks in each PATH directory left to right until it finds "java"
If not found: "command not found" error
```

**Why this matters:** If you install Java manually to `/opt/java/bin/`, you need to add that to PATH so Linux can find it:
```bash
export PATH=$PATH:/opt/java/bin
```

---

## Package Management — Installing Software

Linux uses **package managers** to install, update, and remove software. It's like an app store but from the command line.

**Ubuntu/Debian systems use `apt`:**
```bash
sudo apt update              # refresh the list of available packages
sudo apt install nginx       # install nginx web server
sudo apt install -y java-17  # -y means "yes to all prompts"
sudo apt remove nginx        # uninstall
sudo apt upgrade             # upgrade all installed packages
sudo apt autoremove          # remove packages no longer needed

# Search for packages
apt search "text editor"
apt show nginx              # detailed info about a package
```

**CentOS/RHEL/Fedora use `dnf` (or older `yum`):**
```bash
sudo dnf update
sudo dnf install nginx
sudo dnf remove nginx
```

**The `sudo` prefix:**
Most system-level commands require **root** (administrator) privileges. `sudo` temporarily gives you root powers for one command:
```bash
sudo apt install nginx    # runs apt install as root
sudo systemctl restart nginx
sudo nano /etc/nginx/nginx.conf  # edit a protected config file
```

---

## SSH — Connecting to Remote Servers

SSH (Secure Shell) lets you control a remote Linux server as if you're sitting right at its keyboard. All traffic is encrypted.

```
Your Laptop                   Remote Server
    │                               │
    │  ── SSH connection ──────────►│
    │  (encrypted tunnel)           │
    │                         you get a shell
    │                         and can run commands
```

**Connecting:**
```bash
ssh alice@192.168.1.50         # connect to IP address
ssh alice@myserver.com         # connect to hostname
ssh -p 2222 alice@server.com   # use custom port (default is 22)
ssh -i ~/.ssh/mykey.pem ec2-user@3.14.159.26  # use a specific private key (AWS EC2)
```

**Key-based authentication (more secure than passwords):**
```bash
# Step 1: Generate a key pair on YOUR machine
ssh-keygen -t ed25519 -C "my work key"
# Creates:
#   ~/.ssh/id_ed25519      ← PRIVATE key (NEVER share this!)
#   ~/.ssh/id_ed25519.pub  ← PUBLIC key (safe to share, put on servers)

# Step 2: Copy your public key to the server
ssh-copy-id alice@192.168.1.50
# Or manually: cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys (on server)

# Step 3: Now you can connect without a password!
ssh alice@192.168.1.50
```

**How SSH keys work (simplified):**
```
Public key  → goes on the server (like a padlock)
Private key → stays on your laptop (like the key)

Server: "Prove you have the private key for this public key"
Your machine: signs a challenge with private key → sends proof
Server: verifies the signature with public key → "Yep, let them in"
You never send the private key over the network!
```

**Copying files with SCP:**
```bash
scp report.txt alice@server:/home/alice/     # copy local file TO server
scp alice@server:/var/log/app.log ./         # copy FROM server to current dir
scp -r ./project alice@server:/home/alice/   # copy entire folder
```

**Common SSH pitfall — "Permission denied (publickey)":**
```
Check:
1. Private key file permissions: chmod 600 ~/.ssh/id_ed25519
2. .ssh directory permissions: chmod 700 ~/.ssh
3. Public key is in server's ~/.ssh/authorized_keys
4. Correct username (ec2-user for AWS, ubuntu for Ubuntu, root on some)
5. Correct IP or hostname
6. SSH service is running on server: sudo systemctl status ssh
```

---

## Viewing and Editing Text Files

```bash
# VIEWING
cat file.txt           # dump whole file to screen
less file.txt          # paginated viewer
  # Inside less: arrow keys to scroll, / to search, q to quit
head -50 file.txt      # first 50 lines
tail -50 file.txt      # last 50 lines
tail -f app.log        # live follow (Ctrl+C to stop)

# EDITING with nano (beginner-friendly)
nano /etc/hosts
  # Ctrl+O = save, Ctrl+X = exit, Ctrl+W = search
  # Bottom bar shows all shortcuts

# EDITING with vim (powerful but steep learning curve)
vim /etc/nginx/nginx.conf
  # Press i = enter INSERT mode (now you can type)
  # Press Esc = return to command mode
  # Type :w = save
  # Type :q = quit
  # Type :wq = save and quit
  # Type :q! = quit WITHOUT saving
  # Type /word = search for "word"

# Quick one-liner edits
sed -i 's/old_value/new_value/g' config.txt  # replace text in file
echo "new line" >> config.txt                # append a line
```

---

## System Health and Disk Space

```bash
# DISK SPACE
df -h                  # disk free — shows all mounted filesystems
# Output:
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/sda1        50G   23G   25G  48% /
# /dev/sda2       100G   80G   18G  82% /data

du -sh /var/log/       # disk usage of a folder
du -sh /*              # disk usage of top-level folders

# MEMORY
free -h                # show RAM usage
# Output:
#               total  used  free  available
# Mem:          15Gi   8Gi   2Gi   6Gi

# CPU AND LOAD
uptime                 # how long running + load averages (1/5/15 min avg)
lscpu                  # CPU details (cores, architecture)
nproc                  # number of CPU cores

# HARDWARE INFO
lsblk                  # list block devices (disks)
ip addr                # show network interfaces and IP addresses
cat /etc/os-release    # what Linux distro and version is this?
uname -a               # kernel version and architecture
```

---

## The Mind Map

```
LINUX ESSENTIALS
│
├── FILESYSTEM
│   ├── / (root of everything)
│   ├── /etc → configs (nginx, ssh, hosts)
│   ├── /var/log → log files
│   ├── /home/user → your space
│   ├── /tmp → temporary (wiped on reboot)
│   └── /proc → virtual (running processes)
│
├── NAVIGATION
│   ├── pwd, ls, cd
│   ├── mkdir, touch, cp, mv, rm
│   └── find, locate, which
│
├── READING FILES
│   ├── cat, less, head, tail
│   ├── tail -f (live follow)
│   └── grep (search inside)
│
├── PERMISSIONS
│   ├── rwx for owner/group/others
│   ├── chmod (change permissions)
│   ├── chown (change owner)
│   └── 600=private, 644=config, 755=script
│
├── PROCESSES
│   ├── ps aux (list all)
│   ├── top/htop (live monitor)
│   ├── kill PID (SIGTERM graceful)
│   ├── kill -9 PID (SIGKILL force)
│   └── & and nohup (background)
│
├── PIPES & REDIRECTION
│   ├── | (pipe: chain commands)
│   ├── > (overwrite to file)
│   ├── >> (append to file)
│   └── 2>&1 (merge stderr into stdout)
│
├── SSH
│   ├── ssh user@host (connect)
│   ├── ssh-keygen (generate key pair)
│   ├── Public key → server
│   ├── Private key → stays local
│   └── scp (copy files over SSH)
│
└── PACKAGE MANAGEMENT
    ├── apt update → refresh list
    ├── apt install → install
    └── apt remove → uninstall
```

---

## How This Connects to Other Topics

- **Git** — you run `git` commands from the bash shell. Every `git add`, `git commit`, `git push` is a Linux command.
- **Docker** — Docker containers *are* Linux. When you `docker exec -it my-container bash`, you drop into a Linux shell inside the container and navigate the exact same filesystem hierarchy.
- **CI/CD Pipelines** — pipeline steps are bash scripts running on Linux. Understanding `chmod`, pipes, and environment variables is essential for debugging pipelines.
- **Kubernetes** — pods run Linux containers. `kubectl exec -it pod-name -- bash` drops you into a Linux shell.
- **AWS/Cloud** — EC2 instances are Linux VMs. You SSH in, manage processes, tail logs — all Linux essentials.

---

## Common Beginner Mistakes

1. **Forgetting sudo** — getting "Permission denied" because a command needs root. Add `sudo` in front.
2. **rm -rf with wrong path** — always double-check with `ls` first before `rm -rf`.
3. **Editing file without write permission** — save fails silently in nano. Check permissions first with `ls -la`.
4. **SSH "Permission denied"** — usually wrong key permissions (`chmod 600 ~/.ssh/id_rsa`) or wrong username.
5. **Command not found** — program installed but not in PATH. Use `which programname` or add install dir to PATH.
6. **Lost in directories** — always use `pwd` to check where you are. Use `cd ~` to go home.
7. **grep returning nothing** — might be wrong case. Use `grep -i` for case-insensitive search.

---

## References & Further Learning

### 🎥 Videos (Watch These!)
- **"Linux Command Line Full Course" by tutorialinux** — [https://www.youtube.com/watch?v=ZtqBQ68cfJc](https://www.youtube.com/watch?v=ZtqBQ68cfJc) — 5-hour comprehensive beginner-to-intermediate
- **"60 Linux Commands you NEED to know" by NetworkChuck** — [https://www.youtube.com/watch?v=gd7BXuUQ91w](https://www.youtube.com/watch?v=gd7BXuUQ91w) — fast-paced, practical, fun

### 📖 Articles & Docs
- **The Linux Command Line** (free book online) — [https://linuxcommand.org/tlcl.php](https://linuxcommand.org/tlcl.php) — William Shotts. Best free beginner book. Read chapters 1–10.
- **Linux Journey** (interactive learner) — [https://linuxjourney.com/](https://linuxjourney.com/) — gamified, step-by-step exercises
- **Explain Shell** — [https://explainshell.com/](https://explainshell.com/) — paste any command and get each part explained visually

### 🖼️ Diagrams & Cheatsheets
- **Linux Filesystem Hierarchy diagram** — search "Linux Filesystem Hierarchy Standard diagram" on Google Images — great visual map
- **chmod calculator** — [https://chmod-calculator.com/](https://chmod-calculator.com/) — enter permissions visually and see the number
- **Linux Commands Cheatsheet** — [https://www.gnu.org/software/bash/manual/bash.html](https://www.gnu.org/software/bash/manual/bash.html) — official bash reference

### 🛠️ Practice
- **OverTheWire: Bandit** — [https://overthewire.org/wargames/bandit/](https://overthewire.org/wargames/bandit/) — gamified Linux challenges from level 0; excellent practice
- **TryHackMe Linux Fundamentals** — [https://tryhackme.com/module/linux-fundamentals](https://tryhackme.com/module/linux-fundamentals) — browser-based Linux terminal, no install needed
"""

d['guide'] = NEW_GUIDE
with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"Done! Guide length: {len(NEW_GUIDE)} chars")
print(f"Questions: {len(d['questions'])}, Flashcards: {len(d['flashcards'])}")
