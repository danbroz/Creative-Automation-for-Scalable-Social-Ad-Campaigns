# 🍎 macOS Quick Start

Get up and running in **5 minutes** on your Mac!

## Prerequisites

```bash
# Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install requirements
brew install python@3.11 git docker
```

## Installation

```bash
# 1. Clone repository
git clone git@github.com:danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

# 2. Setup (choose one method)
```

### Option A: Docker (Easiest - 2 minutes)

```bash
# Start Docker Desktop
open -a Docker

# Run application
docker-compose up --build

# Open browser
open http://localhost:8000

# Create campaigns through beautiful UI! 🎨
```

### Option B: Native Python (3 minutes)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your_key_here

# Run
./run.sh examples/campaign_brief_1.json
```

## Your First Campaign

### Web UI (Recommended)
1. Visit **http://localhost:8000**
2. Click **"Create Campaign"**
3. Fill in product details
4. Click **"Create Campaign"**
5. Watch progress in real-time
6. Click **"View Generated Images"** when complete

### Command Line
```bash
# Simple
./run.sh examples/campaign_brief_1.json

# Verbose
./run.sh examples/campaign_brief_1.json --verbose
```

## View Your Assets

```bash
# Open in browser
open http://localhost:8000/output/

# Or open in Finder
open output/
```

## Stop Application

```bash
# Docker
docker-compose down

# Python (Ctrl+C to stop, then)
deactivate  # Exit virtual environment
```

## Verified On

- ✅ macOS 11 Big Sur
- ✅ macOS 12 Monterey
- ✅ macOS 13 Ventura  
- ✅ macOS 14 Sonoma
- ✅ macOS 15 Sequoia
- ✅ Intel Macs (x86_64)
- ✅ Apple Silicon (M1/M2/M3)

## Need More Help?

- 📖 Full macOS Guide: [MACOS_GUIDE.md](MACOS_GUIDE.md)
- 🌐 Cross-Platform: [CROSS_PLATFORM_GUIDE.md](CROSS_PLATFORM_GUIDE.md)
- 📘 Main README: [README.md](README.md)

---

**That's it! You're ready to create amazing ad campaigns on your Mac!** 🚀🍎

