# Cross-Platform Compatibility Guide

This application is fully compatible with **Linux**, **macOS**, and **Windows**.

## 🖥️ Platform Support

### ✅ Supported Operating Systems

- **Linux** (Ubuntu 20.04+, Debian 11+, Fedora 35+, etc.)
- **macOS** (11.0 Big Sur and later)
- **Windows** (10, 11, Server 2019+)

---

## 🚀 Quick Start by Operating System

### 🐳 Docker Method (Recommended - Works Identically on All Platforms)

**Prerequisites:** Install Docker Desktop for your platform (see Prerequisites section below)

```bash
# Clone repository
git clone https://github.com/danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

# Set up environment
cp .env.example .env
# Edit .env file and add your OpenAI API key

# Start the application
docker-compose up --build

# Access the web interface
# Open browser to: http://localhost:8000
```

**That's it!** The Docker method works identically on Ubuntu, macOS, and Windows.

### 🐍 Native Python Method

#### Linux & macOS

```bash
# Clone repository
git clone https://github.com/danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env file and add your OpenAI API key

# Run with Docker (recommended)
docker-compose up --build

# Or run directly
./run.sh examples/campaign_brief_1.json
```

#### Windows (Command Prompt)

```cmd
REM Clone repository
git clone https://github.com/danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

REM Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Set up environment
copy .env.example .env
REM Edit .env file and add your OpenAI API key

REM Run with Docker (recommended)
docker-compose up --build

REM Or run directly
run.bat examples\campaign_brief_1.json
```

#### Windows (PowerShell)

```powershell
# Clone repository
git clone https://github.com/danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set up environment
Copy-Item .env.example .env
# Edit .env file and add your OpenAI API key

# Run with Docker (recommended)
docker-compose up --build

# Or run directly
.\run.ps1 examples\campaign_brief_1.json
```

---

## 📋 Prerequisites by Platform

### 🐳 Docker Method (Recommended)

**All Platforms:**
1. **Docker Desktop**: https://www.docker.com/products/docker-desktop
2. **Git**: https://git-scm.com/downloads

**That's it!** Docker handles all dependencies automatically.

### 🐍 Native Python Method

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-venv python3-pip git

# Fedora/RHEL
sudo dnf install python3 python3-pip git

# Optional: Docker for containerized deployment
sudo apt install docker.io docker-compose  # Ubuntu/Debian
sudo dnf install docker docker-compose     # Fedora/RHEL
```

#### macOS
```bash
# Using Homebrew (recommended)
brew install python@3.11 git

# Or download from:
# - Python: https://www.python.org/downloads/macos/
# - Git: https://git-scm.com/download/mac

# Optional: Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop
```

#### Windows

**Required:**
- **Python 3.11+**: https://www.python.org/downloads/windows/
  - ✅ Check "Add Python to PATH" during installation
- **Git**: https://git-scm.com/download/win

**Optional:**
- **Docker Desktop**: https://www.docker.com/products/docker-desktop (recommended)
- **Windows Terminal**: Modern terminal with better PowerShell support
- **WSL2**: For native Linux experience on Windows

---

## 🔧 Platform-Specific Notes

### Linux

✅ **Works out of the box**
- All Python packages compatible
- Native `pathlib` support
- Docker runs natively
- Shell scripts work as expected

**Permissions:**
```bash
# Make scripts executable
chmod +x run.sh

# Add user to docker group (optional)
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### macOS

✅ **Fully supported**
- Same commands as Linux
- Native Docker Desktop support
- Homebrew simplifies dependency installation

**Notes:**
- Use `python3` instead of `python` on some systems
- Docker Desktop provides GUI management
- M1/M2 Macs: Use native arm64 Docker images

### Windows

✅ **Full compatibility with multiple options**

**Option 1: Native Windows (Recommended)**
- Use `run.bat` for Command Prompt
- Use `run.ps1` for PowerShell
- Docker Desktop for containerization
- All Python code uses cross-platform `pathlib`

**Option 2: WSL2 (Linux on Windows)**
```powershell
# Install WSL2
wsl --install

# Then follow Linux instructions inside WSL
```

**PowerShell Execution Policy:**
If you get an error running `run.ps1`:
```powershell
# Allow running scripts (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Path Separators:**
- Python code automatically handles Windows backslashes (`\`) vs Linux forward slashes (`/`)
- Use `pathlib.Path` which works on all platforms
- Git Bash users: Use forward slashes `/` or double backslashes `\\`

**Line Endings:**
- `.gitattributes` ensures correct line endings automatically
- Git converts LF ↔ CRLF appropriately
- No manual conversion needed

---

## 🐳 Docker Container Usage (All Platforms)

Docker provides **identical behavior** across all operating systems and is the **recommended method** for running the application.

### Installation by Platform

#### Ubuntu/Linux
```bash
# Install Docker
sudo apt update
sudo apt install docker.io docker-compose

# Add user to docker group (optional - avoids using sudo)
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect

# Verify installation
docker --version
docker-compose --version
```

#### macOS
```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Or using Homebrew
brew install --cask docker

# Start Docker Desktop
open -a Docker

# Verify installation
docker --version
docker-compose --version
```

#### Windows
```powershell
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Enable WSL2 integration (recommended)
# Docker Desktop will prompt you to enable this

# Verify installation
docker --version
docker-compose --version
```

### 🚀 Running the Application with Docker

#### Step 1: Clone and Setup
```bash
# Clone repository
git clone https://github.com/danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

# Copy environment file
cp .env.example .env
```

#### Step 2: Configure Environment
Edit the `.env` file and add your OpenAI API key:
```bash
# Linux/macOS
nano .env

# Windows (Command Prompt)
notepad .env

# Windows (PowerShell)
notepad .env
```

Add your API key:
```env
OPENAI_API_KEY=your-api-key-here
```

#### Step 3: Start the Application
```bash
# Build and start the container
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

#### Step 4: Access the Application
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### 🛠️ Docker Commands

#### Basic Operations
```bash
# Start application
docker-compose up

# Start in background (detached)
docker-compose up -d

# Stop application
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild containers
docker-compose up --build

# View logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs creative-automation-api
```

#### Development Commands
```bash
# Run with live reload (if configured)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Execute commands inside container
docker-compose exec creative-automation-api bash

# Run tests inside container
docker-compose exec creative-automation-api python -m pytest

# Check container status
docker-compose ps

# View container resource usage
docker stats
```

#### Troubleshooting Commands
```bash
# Check container logs
docker-compose logs --tail=50

# Restart specific service
docker-compose restart creative-automation-api

# Remove all containers and images
docker-compose down --rmi all

# Clean up unused Docker resources
docker system prune -a
```

### 📁 Docker Volume Management

The application uses Docker volumes for data persistence:

```bash
# View volumes
docker volume ls

# Inspect volume
docker volume inspect creatve-automation-for-scalable-social-ad-campaigns_creative-automation-db

# Backup database
docker-compose exec creative-automation-api cp /app/creative_automation.db /app/backup.db
docker cp $(docker-compose ps -q creative-automation-api):/app/backup.db ./creative_automation_backup.db

# Restore database
docker cp ./creative_automation_backup.db $(docker-compose ps -q creative-automation-api):/app/creative_automation.db
docker-compose restart creative-automation-api
```

### 🔧 Docker Configuration

#### Environment Variables
The application uses these environment variables (set in `.env` file):

```env
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional
DATABASE_URL=sqlite:///./creative_automation.db
LOG_LEVEL=INFO
API_KEY=test-key
```

#### Port Configuration
Default ports (can be changed in `docker-compose.yml`):
- **Web Interface**: 8000
- **API**: 8000

To change ports, edit `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Change 8080 to your preferred port
```

### 🐛 Docker Troubleshooting

#### Common Issues

**Issue: Port already in use**
```bash
# Check what's using the port
# Linux/macOS
lsof -i :8000

# Windows
netstat -ano | findstr :8000

# Change port in docker-compose.yml
```

**Issue: Permission denied (Linux)**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

**Issue: Docker Desktop not running (macOS/Windows)**
```bash
# Start Docker Desktop application
# macOS: open -a Docker
# Windows: Start Docker Desktop from Start menu
```

**Issue: Out of disk space**
```bash
# Clean up Docker resources
docker system prune -a
docker volume prune
```

**Issue: Container won't start**
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down --rmi all
docker-compose up --build
```

### 🚀 Production Deployment

#### Using Docker Compose
```bash
# Production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# With custom environment file
docker-compose --env-file .env.production up -d
```

#### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml creative-automation
```

#### Using Kubernetes
```bash
# Generate Kubernetes manifests
kompose convert

# Apply to cluster
kubectl apply -f .
```

---

## 🗃️ Database (SQLite)

✅ **SQLite works identically on all platforms**

- Single file database: `creative_automation.db`
- No server required
- Portable across operating systems
- Same SQL syntax everywhere

**Backup (All Platforms):**
```bash
# Simply copy the database file
cp creative_automation.db creative_automation.backup.db  # Linux/Mac
copy creative_automation.db creative_automation.backup.db  # Windows
```

---

## 📁 File Paths

All Python code uses `pathlib.Path` which automatically handles platform differences:

```python
from pathlib import Path

# Works on all platforms - automatically uses correct separator
output_dir = Path("output") / "campaign" / "product"
# Linux/Mac: output/campaign/product
# Windows:   output\campaign\product
```

---

## ✅ What's Cross-Platform

- ✅ **All Python code** - Uses `pathlib` for paths
- ✅ **Docker containers** - Identical on all platforms
- ✅ **SQLite database** - Single portable file
- ✅ **Web interface** - Browser-based, OS-independent
- ✅ **API endpoints** - HTTP protocol, universal
- ✅ **Environment variables** - `.env` file works everywhere
- ✅ **Virtual environments** - Python's venv on all platforms

---

## 🧪 Testing on Each Platform

### Verify Installation

**All Platforms:**
```bash
# Check Python version
python --version  # Should be 3.11+

# Check Docker
docker --version
docker-compose --version

# Check Git
git --version
```

### Run Test Campaign

**Linux/macOS:**
```bash
./run.sh examples/campaign_brief_1.json --verbose
```

**Windows (CMD):**
```cmd
run.bat examples\campaign_brief_1.json --verbose
```

**Windows (PowerShell):**
```powershell
.\run.ps1 examples\campaign_brief_1.json --verbose
```

**Docker (All Platforms):**
```bash
docker-compose up
# Then visit http://localhost:8000 and create a campaign
```

---

## 🐛 Troubleshooting by Platform

### Linux

**Issue:** Permission denied for `run.sh`
```bash
chmod +x run.sh
```

**Issue:** Docker permission denied
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### macOS

**Issue:** `python` not found
```bash
# Use python3 instead
python3 -m venv venv
```

**Issue:** Docker not running
```bash
# Start Docker Desktop application
open -a Docker
```

### Windows

**Issue:** `run.ps1` execution policy error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue:** Python not in PATH
- Reinstall Python
- Check "Add Python to PATH" during installation

**Issue:** Line ending errors (CRLF vs LF)
```bash
# Git will handle automatically with .gitattributes
# Or configure Git:
git config --global core.autocrlf true  # Windows
```

**Issue:** Docker can't start containers
- Enable Hyper-V and WSL2 in Windows Features
- Or install WSL2: `wsl --install`

---

## 📊 Performance Notes

### Linux
- **Best performance** for Docker (native)
- Direct filesystem access
- Lower overhead

### macOS
- Docker Desktop uses lightweight VM
- Slightly higher overhead than Linux
- M1/M2 excellent performance with arm64 images

### Windows
- Docker Desktop uses WSL2 backend (recommended)
- Near-native Linux performance with WSL2
- Hyper-V mode has more overhead
- Use WSL2 for best performance

---

## 🎯 Recommended Setup by Use Case

### Development
- **Linux/macOS**: Native Python + Docker
- **Windows**: WSL2 + Docker Desktop OR Native Python + Docker Desktop

### Production
- **All Platforms**: Docker (ensures consistency)
- **Cloud**: Docker + Kubernetes (platform-independent)

### Simple Testing
- **All Platforms**: Native Python + virtual environment

---

## 🔐 Security Notes

### File Permissions

**Linux/macOS:**
```bash
# Secure .env file
chmod 600 .env

# Secure private keys
chmod 600 *.pem
```

**Windows:**
```powershell
# Use File Explorer -> Properties -> Security
# Or PowerShell:
$acl = Get-Acl .env
$acl.SetAccessRuleProtection($true, $false)
Set-Acl .env $acl
```

---

## 📚 Additional Resources

- **Python Docs**: https://docs.python.org/3/
- **Docker Docs**: https://docs.docker.com/
- **WSL2 Guide**: https://docs.microsoft.com/en-us/windows/wsl/
- **Git Bash**: https://gitforwindows.org/

---

## ✅ Verified Platforms

This application has been tested on:

- ✅ Ubuntu 20.04, 22.04
- ✅ Debian 11, 12
- ✅ macOS 12 Monterey, 13 Ventura, 14 Sonoma
- ✅ Windows 10 (21H2+)
- ✅ Windows 11
- ✅ Windows Server 2019, 2022
- ✅ Docker Desktop (all platforms)
- ✅ WSL2 (Ubuntu, Debian)

---

**Need help?** Check the main [README.md](../README.md) or open an issue on GitHub.

