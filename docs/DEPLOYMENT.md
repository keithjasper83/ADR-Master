# Deployment Guide

This guide covers deploying ADR-Master in various environments.

## Quick Start Options

### Option 1: Docker (Recommended)

```bash
# Build
docker build -t adr-master .

# Run
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/ADR:/app/ADR \
  -v $(pwd)/_logs:/app/_logs \
  --env-file .env \
  --name adr-master \
  adr-master

# View logs
docker logs -f adr-master

# Stop
docker stop adr-master
```

### Option 2: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  adr-master:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./ADR:/app/ADR
      - ./_logs:/app/_logs
      - ./adr_master.db:/app/adr_master.db
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Local LLM (Ollama)
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

Run with:
```bash
docker-compose up -d
```

### Option 3: Local Python

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install
pip install -e .

# Run
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Option 4: Devcontainer (VS Code)

1. Open folder in VS Code
2. Install "Remote - Containers" extension
3. Click "Reopen in Container"
4. Application starts automatically

## Production Deployment

### Behind Reverse Proxy

#### Nginx

Create `/etc/nginx/sites-available/adr-master`:

```nginx
server {
    listen 80;
    server_name adr-master.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed later)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/adr-master /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Caddy (Easier)

Create `Caddyfile`:

```
adr-master.yourdomain.com {
    reverse_proxy localhost:8000
}
```

Run:
```bash
caddy run
```

### Systemd Service

Create `/etc/systemd/system/adr-master.service`:

```ini
[Unit]
Description=ADR-Master Service
After=network.target

[Service]
Type=simple
User=adr-master
WorkingDirectory=/opt/adr-master
Environment="PATH=/opt/adr-master/venv/bin"
ExecStart=/opt/adr-master/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable adr-master
sudo systemctl start adr-master
sudo systemctl status adr-master
```

## Environment Configuration

### Production .env

```env
# Application
WORKDIR=/opt/adr-master
DEBUG=false

# Database
DATABASE_URL=sqlite:////opt/adr-master/adr_master.db

# MCP (if used)
MCP_BASE_URL=https://mcp.yourdomain.com/api
MCP_TOKEN=production-token-here

# LLM
LLM_ENDPOINT=http://localhost:11434/api/generate

# GitHub (if used)
GITHUB_TOKEN=ghp_productiontoken

# Security
CSRF_SECRET=generate-long-random-string-here
CORS_ENABLED=false

# Logging
LOG_LEVEL=INFO
LOG_DIR=/opt/adr-master/_logs
```

### Security Best Practices

1. **Generate strong secrets:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Set proper permissions:**
   ```bash
   chmod 600 .env
   chmod 700 ADR/
   chmod 700 _logs/
   ```

3. **Run as non-root user:**
   ```bash
   sudo useradd -r -s /bin/false adr-master
   sudo chown -R adr-master:adr-master /opt/adr-master
   ```

4. **Enable firewall:**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

## Kubernetes Deployment

### Basic Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adr-master
spec:
  replicas: 1
  selector:
    matchLabels:
      app: adr-master
  template:
    metadata:
      labels:
        app: adr-master
    spec:
      containers:
      - name: adr-master
        image: adr-master:latest
        ports:
        - containerPort: 8000
        env:
        - name: WORKDIR
          value: /app
        - name: DATABASE_URL
          value: sqlite:///./adr_master.db
        volumeMounts:
        - name: adr-data
          mountPath: /app/ADR
        - name: logs
          mountPath: /app/_logs
      volumes:
      - name: adr-data
        persistentVolumeClaim:
          claimName: adr-data-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: adr-logs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: adr-master
spec:
  selector:
    app: adr-master
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

Apply:
```bash
kubectl apply -f k8s/
```

## Monitoring

### Health Checks

```bash
# Simple check
curl http://localhost:8000/healthz

# Detailed check with monitoring
curl -f http://localhost:8000/healthz || systemctl restart adr-master
```

### Logging

Logs are stored in:
- Application logs: `_logs/adr.jsonl`
- System logs: `journalctl -u adr-master -f`
- Docker logs: `docker logs adr-master`

### Metrics

For production monitoring, consider:
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Sentry for error tracking

## Backup Strategy

### Database Backup

```bash
# Daily backup
sqlite3 adr_master.db ".backup /backups/adr_master_$(date +%Y%m%d).db"

# Compress old backups
find /backups -name "*.db" -mtime +7 -exec gzip {} \;
```

### Full Backup Script

Create `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR=/backups/adr-master
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sqlite3 /opt/adr-master/adr_master.db ".backup $BACKUP_DIR/db_$DATE.db"

# Backup ADRs
tar -czf $BACKUP_DIR/adr_$DATE.tar.gz /opt/adr-master/ADR/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /opt/adr-master/_logs/

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: $DATE"
```

Add to cron:
```bash
0 2 * * * /opt/adr-master/backup.sh
```

## Scaling Considerations

### Single User / Small Team
- Docker or local Python installation sufficient
- SQLite works well
- No special configuration needed

### Medium Team (5-20 users)
- Use reverse proxy (Nginx/Caddy)
- Consider PostgreSQL instead of SQLite
- Add monitoring and alerting
- Regular backups

### Large Team / Enterprise
- Kubernetes deployment
- Separate database (PostgreSQL/MySQL)
- Load balancer
- High availability setup
- Distributed logging
- Security hardening

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Locked

```bash
# Check for other processes
ps aux | grep uvicorn

# Stop all instances
pkill -f uvicorn

# Restart
systemctl restart adr-master
```

### Permission Denied

```bash
# Fix ownership
sudo chown -R adr-master:adr-master /opt/adr-master

# Fix permissions
chmod 755 /opt/adr-master
chmod 644 /opt/adr-master/ADR/**/*.md
```

## Upgrades

### Docker

```bash
# Pull new image
docker pull adr-master:latest

# Stop old container
docker stop adr-master
docker rm adr-master

# Start new container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/ADR:/app/ADR \
  --name adr-master \
  adr-master:latest
```

### Local Installation

```bash
# Backup first
./backup.sh

# Pull changes
git pull origin main

# Update dependencies
pip install -e . --upgrade

# Restart service
systemctl restart adr-master
```

## Security Checklist

- [ ] `.env` file has secure permissions (600)
- [ ] Strong `CSRF_SECRET` generated
- [ ] HTTPS enabled via reverse proxy
- [ ] Firewall configured
- [ ] Running as non-root user
- [ ] Regular backups configured
- [ ] Log rotation enabled
- [ ] MCP/GitHub tokens secured
- [ ] CORS properly configured
- [ ] Database file protected

## Support

For deployment issues:
- Check logs: `docker logs adr-master` or `journalctl -u adr-master`
- Verify health: `curl http://localhost:8000/healthz`
- Review configuration in `.env`
- See troubleshooting section above
