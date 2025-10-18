# Troubleshooting Guide

## Docker Compose Errors

### Error: `KeyError: 'ContainerConfig'`

**Symptoms:**
```
KeyError: 'ContainerConfig'
ERROR: for api  'ContainerConfig'
```

**Cause:**
- Conflict with existing containers
- Incompatibility between docker-compose version and container state

**Solution 1: Remove old containers and try again**
```bash
# Stop and remove all containers
docker-compose down

# Remove any orphaned containers
docker container prune -f

# Start fresh
docker-compose up --build
```

**Solution 2: If Solution 1 doesn't work, clean up Docker**
```bash
# Stop all running containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images (optional, will need to rebuild)
docker rmi $(docker images -q)

# Start fresh
docker-compose up --build
```

**Solution 3: Update docker-compose (recommended)**
```bash
# Check current version
docker-compose --version

# On Ubuntu/Debian - install latest docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify new version
docker-compose --version

# Should show v2.x.x or higher
```

**Solution 4: Use Docker Compose V2 (modern syntax)**
```bash
# Instead of: docker-compose up --build
# Use: docker compose up --build (note the space, not hyphen)

docker compose down
docker compose up --build
```

## Port Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solution:**
```bash
# Find what's using port 8000
sudo lsof -i :8000

# Or on some systems:
sudo netstat -tulpn | grep :8000

# Kill the process or change port in docker-compose.yml
# Change: "8000:8000" to "8080:8000" (or any other available port)
```

## Permission Denied Errors

**Error:**
```
Permission denied
```

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then test:
docker ps

# If still issues, run with sudo temporarily:
sudo docker-compose up --build
```

## Out of Disk Space

**Error:**
```
no space left on device
```

**Solution:**
```bash
# Clean up Docker resources
docker system prune -a
docker volume prune

# Check disk usage
docker system df
df -h
```

## Container Won't Start

**Check logs:**
```bash
# View logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs creative-automation-api
```

## Database Issues

**SQLite database locked:**
```bash
# Stop containers
docker-compose down

# Remove database file
rm creative_automation.db*

# Start fresh
docker-compose up --build
```

## API Key Issues

**Check environment file:**
```bash
# Verify .env file exists
cat .env

# Should contain:
# OPENAI_API_KEY=your-api-key-here

# Check if container can see it
docker-compose exec creative-automation-api env | grep OPENAI
```

## Quick Fix for Most Issues

**Nuclear option - complete reset:**
```bash
# Stop everything
docker-compose down -v

# Remove containers
docker container prune -f

# Remove images
docker image prune -a -f

# Remove volumes
docker volume prune -f

# Start fresh
docker-compose up --build
```

## Getting Help

If none of these solutions work:

1. Check Docker version: `docker --version` (should be 20.x or higher)
2. Check docker-compose version: `docker-compose --version` (should be 1.29+ or use v2)
3. Check system resources: `df -h` and `free -h`
4. Collect logs: `docker-compose logs > error.log`
5. Open an issue on GitHub with:
   - Your OS version
   - Docker version
   - docker-compose version
   - Error logs
   - Steps to reproduce

## Platform-Specific Issues

### Linux
- Ensure Docker daemon is running: `sudo systemctl status docker`
- Check user permissions: `groups` (should include 'docker')

### macOS
- Ensure Docker Desktop is running
- Check Docker Desktop settings for resource allocation
- Try restarting Docker Desktop

### Windows
- Ensure WSL2 is enabled for Docker Desktop
- Check Docker Desktop is using WSL2 backend (not Hyper-V)
- Try restarting Docker Desktop

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Project README](README.md)
- [Docker Guide](docs/DOCKER_GUIDE.md)
