# Docker Container Guide

This guide provides comprehensive instructions for running the Creative Automation Platform using Docker containers on Ubuntu, macOS, and Windows.

## 🎯 Why Use Docker?

- ✅ **Identical behavior** across all operating systems
- ✅ **No dependency conflicts** - everything is containerized
- ✅ **Easy setup** - just install Docker and run
- ✅ **Production-ready** - same container works in development and production
- ✅ **Isolated environment** - doesn't affect your system

## 📋 Prerequisites

### All Platforms
1. **Docker Desktop**: https://www.docker.com/products/docker-desktop
2. **Git**: https://git-scm.com/downloads
3. **OpenAI API Key**: Get from https://platform.openai.com/api-keys

## 🚀 Quick Start (All Platforms)

```bash
# 1. Clone the repository
git clone https://github.com/danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

# 2. Set up environment
cp .env.example .env

# 3. Edit .env file and add your OpenAI API key
# OPENAI_API_KEY=your-api-key-here

# 4. Start the application
docker-compose up --build

# 5. Access the web interface
# Open browser to: http://localhost:8000
```

**That's it!** The application is now running in a container.

## 🖥️ Platform-Specific Installation

### Ubuntu/Linux

#### Install Docker
```bash
# Update package index
sudo apt update

# Install Docker
sudo apt install docker.io docker-compose

# Add user to docker group (optional - avoids using sudo)
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect

# Verify installation
docker --version
docker-compose --version
```

#### Start Docker Service
```bash
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

### macOS

#### Install Docker Desktop
```bash
# Using Homebrew (recommended)
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop
```

#### Start Docker Desktop
```bash
# Start Docker Desktop application
open -a Docker

# Verify installation
docker --version
docker-compose --version
```

### Windows

#### Install Docker Desktop
1. Download from: https://www.docker.com/products/docker-desktop
2. Run the installer
3. Enable WSL2 integration when prompted (recommended)
4. Restart your computer if required

#### Verify Installation
```powershell
# Open PowerShell or Command Prompt
docker --version
docker-compose --version
```

## 🛠️ Docker Commands Reference

### Basic Operations

```bash
# Start the application
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Build and start (rebuild containers)
docker-compose up --build

# Stop the application
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs creative-automation-api
```

### Development Commands

```bash
# Execute commands inside container
docker-compose exec creative-automation-api bash

# Run tests inside container
docker-compose exec creative-automation-api python -m pytest

# Check container status
docker-compose ps

# View container resource usage
docker stats

# Restart specific service
docker-compose restart creative-automation-api
```

### Troubleshooting Commands

```bash
# Check container logs
docker-compose logs --tail=50

# Remove all containers and images
docker-compose down --rmi all

# Clean up unused Docker resources
docker system prune -a

# Remove all volumes
docker volume prune

# Check Docker system info
docker system df
```

## 🔧 Configuration

### Environment Variables

The application uses these environment variables (set in `.env` file):

```env
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional
DATABASE_URL=sqlite:///./creative_automation.db
LOG_LEVEL=INFO
API_KEY=test-key
```

### Port Configuration

Default ports (can be changed in `docker-compose.yml`):
- **Web Interface**: 8000
- **API**: 8000

To change ports, edit `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Change 8080 to your preferred port
```

### Volume Mounts

The application uses these volumes:
- `./creative_automation.db:/app/creative_automation.db` - Database persistence
- `./output:/app/output` - Generated assets
- `./logs:/app/logs` - Application logs

## 📁 Data Management

### Backup Database

```bash
# Create backup
docker-compose exec creative-automation-api cp /app/creative_automation.db /app/backup.db
docker cp $(docker-compose ps -q creative-automation-api):/app/backup.db ./creative_automation_backup.db

# Or backup the entire volume
docker run --rm -v creatve-automation-for-scalable-social-ad-campaigns_creative-automation-db:/data -v $(pwd):/backup alpine tar czf /backup/db_backup.tar.gz -C /data .
```

### Restore Database

```bash
# Restore from backup
docker cp ./creative_automation_backup.db $(docker-compose ps -q creative-automation-api):/app/creative_automation.db
docker-compose restart creative-automation-api
```

### Access Generated Assets

```bash
# View generated assets
ls -la output/

# Copy assets out of container
docker cp $(docker-compose ps -q creative-automation-api):/app/output ./local_output
```

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
# Linux/macOS
lsof -i :8000

# Windows
netstat -ano | findstr :8000

# Change port in docker-compose.yml
```

#### Permission Denied (Linux)
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in

# Or run with sudo
sudo docker-compose up
```

#### Docker Desktop Not Running (macOS/Windows)
```bash
# Start Docker Desktop application
# macOS: open -a Docker
# Windows: Start Docker Desktop from Start menu
```

#### Out of Disk Space
```bash
# Clean up Docker resources
docker system prune -a
docker volume prune

# Check disk usage
docker system df
```

#### Container Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down --rmi all
docker-compose up --build

# Check container status
docker-compose ps
```

#### API Key Issues
```bash
# Verify .env file exists and has correct API key
cat .env

# Check if container can access the API key
docker-compose exec creative-automation-api env | grep OPENAI
```

### Performance Issues

#### Slow Startup
```bash
# Use cached layers
docker-compose up --build

# Or build without cache
docker-compose build --no-cache
```

#### High Memory Usage
```bash
# Check container resource usage
docker stats

# Limit container resources in docker-compose.yml
services:
  creative-automation-api:
    deploy:
      resources:
        limits:
          memory: 2G
```

## 🚀 Production Deployment

### Using Docker Compose

```bash
# Production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# With custom environment file
docker-compose --env-file .env.production up -d
```

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml creative-automation

# Check service status
docker service ls
```

### Using Kubernetes

```bash
# Generate Kubernetes manifests
kompose convert

# Apply to cluster
kubectl apply -f .

# Check deployment
kubectl get pods
```

## 🔐 Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use strong API keys
- Rotate keys regularly

### Container Security
```bash
# Run as non-root user (already configured)
# Use specific image tags instead of 'latest'
# Regularly update base images
```

### Network Security
```bash
# Use internal networks for container communication
# Expose only necessary ports
# Use reverse proxy for production
```

## 📊 Monitoring

### Health Checks

```bash
# Check application health
curl http://localhost:8000/api/v1/health

# Check container health
docker-compose ps
```

### Logs

```bash
# View application logs
docker-compose logs -f creative-automation-api

# View system logs
docker system events
```

### Metrics

```bash
# Container resource usage
docker stats

# Disk usage
docker system df
```

## 🎯 Best Practices

### Development
- Use `docker-compose up --build` for development
- Mount source code as volume for live reloading
- Use `.dockerignore` to exclude unnecessary files

### Production
- Use specific image tags
- Set resource limits
- Use health checks
- Implement proper logging
- Use secrets management

### Maintenance
- Regularly update base images
- Clean up unused resources
- Monitor disk usage
- Backup data regularly

## 📚 Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose Reference**: https://docs.docker.com/compose/
- **Docker Security**: https://docs.docker.com/engine/security/
- **Best Practices**: https://docs.docker.com/develop/dev-best-practices/

## ✅ Verification

After following this guide, you should be able to:

- ✅ Start the application with `docker-compose up --build`
- ✅ Access the web interface at http://localhost:8000
- ✅ Create campaigns through the UI
- ✅ View generated assets in the `output/` directory
- ✅ Check logs with `docker-compose logs`
- ✅ Stop the application with `docker-compose down`

## 🆘 Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify Docker is running: `docker --version`
3. Check the troubleshooting section above
4. Open an issue on GitHub with:
   - Your operating system
   - Docker version
   - Error logs
   - Steps to reproduce

---

**Happy containerizing!** 🐳
