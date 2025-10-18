# macOS Installation & Usage Guide

Complete guide for running Creative Automation Pipeline on **macOS** (Big Sur, Monterey, Ventura, Sonoma, Sequoia).

## 🍎 macOS Support

This application is **fully tested and optimized** for macOS, including:

- ✅ macOS 11 (Big Sur)
- ✅ macOS 12 (Monterey)
- ✅ macOS 13 (Ventura)
- ✅ macOS 14 (Sonoma)
- ✅ macOS 15 (Sequoia)
- ✅ Intel (x86_64) and Apple Silicon (M1/M2/M3) Macs

---

## 🚀 Quick Start for macOS

### Prerequisites

1. **Install Homebrew** (if not already installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install Python 3.11+**:
```bash
brew install python@3.11
```

3. **Install Git**:
```bash
brew install git
```

4. **Install Docker Desktop** (Optional but Recommended):
- Download from: https://www.docker.com/products/docker-desktop
- Or via Homebrew: `brew install --cask docker`

---

## 📦 Installation

### Method 1: Docker (Recommended)

```bash
# Clone repository
git clone git@github.com:danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

# Start with Docker
docker-compose up --build

# Access at http://localhost:8000
```

### Method 2: Native Python

```bash
# Clone repository
git clone git@github.com:danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run web interface
uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# Or run a campaign directly
./run.sh examples/campaign_brief_1.json
```

---

## 🔧 macOS-Specific Configuration

### Python Version

macOS may have both `python` and `python3` commands:

```bash
# Check Python version
python3 --version  # Should be 3.11+

# If python command doesn't work, use python3
python3 -m venv venv
```

### Shell Configuration

**Default Shell (zsh on macOS Catalina+):**

The `run.sh` script works with both bash and zsh:

```bash
# Make script executable (one time)
chmod +x run.sh

# Run campaign
./run.sh examples/campaign_brief_1.json
```

**Add to PATH (Optional):**

Add this to `~/.zshrc` (for zsh) or `~/.bash_profile` (for bash):

```bash
# Creative Automation Pipeline
alias creative-automation='cd ~/path/to/Creatve-Automation-for-Scalable-Social-Ad-Campaigns && source venv/bin/activate'
```

Then run:
```bash
source ~/.zshrc  # or ~/.bash_profile
creative-automation
```

### File System Notes

macOS uses **case-insensitive** file system by default (unless using APFS with case sensitivity):

- File paths work the same as Linux
- Uses forward slashes `/` like Linux
- No special handling needed

---

## 🐳 Docker on macOS

### Installation

**Option 1: Docker Desktop (GUI)**
- Download: https://www.docker.com/products/docker-desktop
- Provides GUI management
- Includes Docker Compose

**Option 2: Homebrew**
```bash
brew install --cask docker
```

### Usage

```bash
# Start Docker Desktop (if not auto-started)
open -a Docker

# Wait for Docker to start (whale icon in menu bar)

# Run application
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns
docker-compose up --build

# Access web interface
open http://localhost:8000

# Stop application
docker-compose down
```

### Docker Performance on macOS

**Intel Macs:**
- Docker uses HyperKit VM
- Slightly slower than Linux
- Still excellent performance

**Apple Silicon (M1/M2/M3) Macs:**
- Docker uses native ARM64 support
- Excellent performance
- May see "platform linux/amd64" warnings (safe to ignore)
- Our images work on both x86_64 and arm64

---

## 🎯 Running Campaigns on macOS

### Web Interface (Recommended)

```bash
# Start application
docker-compose up

# Open browser
open http://localhost:8000

# Create campaign through UI
```

### Command Line

```bash
# Activate virtual environment
source venv/bin/activate

# Run campaign
./run.sh examples/campaign_brief_1.json --verbose

# Or directly with Python
python -m src.main examples/campaign_brief_1.json
```

---

## 🔍 Troubleshooting macOS

### Issue: `python3` command not found

**Solution:**
```bash
# Install Python via Homebrew
brew install python@3.11

# Or download from python.org
open https://www.python.org/downloads/macos/
```

### Issue: Permission denied for `run.sh`

**Solution:**
```bash
chmod +x run.sh
```

### Issue: `xcrun: error: invalid active developer path`

This happens after macOS updates. **Solution:**

```bash
xcode-select --install
```

### Issue: Docker Desktop won't start

**Solutions:**

1. Check system requirements (macOS 11+)
2. Enable Virtualization in Security & Privacy
3. Restart Mac
4. Reinstall Docker Desktop

```bash
# Uninstall
brew uninstall --cask docker

# Reinstall
brew install --cask docker
```

### Issue: Port 8000 already in use

**Solution:**

```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
docker-compose -f docker-compose.yml -e "PORT=8080" up
```

### Issue: Slow Docker on macOS

**Optimization:**

1. **Increase Docker Resources:**
   - Docker Desktop → Preferences → Resources
   - Increase CPU and Memory allocation

2. **Use Docker Volume for Database:**
   - Already configured in `docker-compose.yml`
   - Uses named volume for better performance

3. **Disable VirtioFS (if on Intel Mac):**
   - Docker Desktop → Preferences → Experimental Features
   - Disable VirtioFS

---

## 📂 File Locations on macOS

### Default Paths

```bash
# Application
~/Creatve-Automation-for-Scalable-Social-Ad-Campaigns/

# Virtual Environment
~/Creatve-Automation-for-Scalable-Social-Ad-Campaigns/venv/

# Database
~/Creatve-Automation-for-Scalable-Social-Ad-Campaigns/creative_automation.db

# Generated Assets
~/Creatve-Automation-for-Scalable-Social-Ad-Campaigns/output/

# Logs
~/Creatve-Automation-for-Scalable-Social-Ad-Campaigns/logs/
```

### Open in Finder

```bash
# Open project directory
open .

# Open output directory
open output/

# Open specific campaign
open output/summer_wellness_2025/
```

---

## 🎨 macOS Native Features

### Finder Integration

**Quick Look Preview:**
- Select image in Finder
- Press Space to preview
- Works with generated PNG files

**Tags:**
```bash
# Tag campaign folders
tag -a "Campaign,Generated" output/summer_wellness_2025/
```

### Spotlight Search

```bash
# Index output directory for Spotlight
mdimport output/
```

### Notifications

Add to script for completion notifications:

```bash
# Add to run.sh for macOS notifications
osascript -e 'display notification "Campaign completed!" with title "Creative Automation"'
```

---

## 🔐 Security on macOS

### Secure .env File

```bash
# Restrict permissions
chmod 600 .env

# Verify
ls -la .env
# Should show: -rw------- (only owner can read/write)
```

### Gatekeeper

If macOS blocks the application:

```bash
# Allow in System Preferences > Security & Privacy
# Or use this command:
xattr -d com.apple.quarantine run.sh
```

---

## 🚄 Performance Tips for macOS

### 1. Use Docker for Best Performance

Docker on Apple Silicon is extremely fast:

```bash
docker-compose up --build
```

### 2. Optimize Python Virtual Environment

```bash
# Create venv with optimizations
python3 -m venv --upgrade-deps venv

# Use PyPy for even better performance (optional)
brew install pypy3
pypy3 -m venv venv-pypy
```

### 3. Use SSD for Output Directory

If you have multiple drives, store output on SSD:

```bash
# Create symlink to SSD
ln -s /path/to/ssd/output output
```

---

## 📊 Monitoring on macOS

### Activity Monitor

```bash
# Open Activity Monitor
open -a "Activity Monitor"

# Or use terminal
top -o cpu  # Sort by CPU
top -o mem  # Sort by memory
```

### Docker Stats

```bash
# Monitor Docker containers
docker stats

# Monitor specific container
docker stats creative-automation-api
```

---

## 🍺 Homebrew Maintenance

Keep your system updated:

```bash
# Update Homebrew
brew update

# Upgrade packages
brew upgrade

# Cleanup old versions
brew cleanup

# Check for issues
brew doctor
```

---

## 🎓 macOS Best Practices

### 1. Use Homebrew for Dependencies

Better than manual installations:
- Automatic updates
- Easy management
- System-wide availability

### 2. Use Docker for Deployment

Most reliable across macOS versions:
- Consistent environment
- Easy updates
- Isolated dependencies

### 3. Backup Database

```bash
# Simple backup
cp creative_automation.db creative_automation.backup.db

# Time Machine backup (automatic)
# Ensure project directory is not excluded
```

### 4. Use Terminal Multiplexer

```bash
# Install tmux or iTerm2 for better terminal management
brew install tmux
# or
brew install --cask iterm2
```

---

## 🔄 Updating on macOS

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Rebuild Docker (if using)
docker-compose build --no-cache
docker-compose up
```

---

## 🎯 macOS Keyboard Shortcuts

Useful shortcuts when working with the application:

- `⌘ + T` - New Terminal tab
- `⌘ + W` - Close Terminal tab
- `⌘ + Space` - Spotlight search
- `Ctrl + C` - Stop running process
- `Ctrl + Z` - Pause process
- `Ctrl + D` - Exit shell/deactivate venv

---

## 📱 iOS Integration (Future)

The web interface works on iOS Safari:
- Visit `http://your-mac-ip:8000` from iPhone/iPad
- Responsive design works on all screen sizes
- Bookmark for quick access

---

## ✅ Verified macOS Versions

Tested and working on:

- ✅ macOS 11 Big Sur (Intel & M1)
- ✅ macOS 12 Monterey (Intel & M1)
- ✅ macOS 13 Ventura (Intel & M1/M2)
- ✅ macOS 14 Sonoma (Intel & M1/M2/M3)
- ✅ macOS 15 Sequoia (M1/M2/M3)

**CPU Architecture:**
- ✅ Intel x86_64 (all Mac models 2006-2020)
- ✅ Apple Silicon ARM64 (M1, M2, M3 - 2020+)

---

## 🆘 Getting Help

1. Check [CROSS_PLATFORM_GUIDE.md](CROSS_PLATFORM_GUIDE.md)
2. Review [README.md](../README.md)
3. Open issue on GitHub
4. Include macOS version and error logs

**Collect System Info:**
```bash
# macOS version
sw_vers

# Python version
python3 --version

# Docker version
docker --version

# Homebrew packages
brew list
```

---

**Enjoy Creative Automation on your Mac!** 🚀🍎

