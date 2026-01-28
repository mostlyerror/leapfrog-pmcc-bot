# Deployment Guide

Complete guide for deploying PMCC Bot to various environments.

## Overview

PMCC Bot can run on:
- **Local machine** (development/testing)
- **Linux VPS** (DigitalOcean, Linode, AWS EC2)
- **Railway** (recommended for cloud, free tier)
- **Render** (alternative cloud platform)
- **Docker** (any Docker-compatible environment)

---

## 1. Railway Deployment (Recommended)

**Pros**: Free tier, automatic restarts, built-in logging, persistent storage
**Cons**: Requires credit card on file (no charges on free tier)

### Steps:

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Initialize Project**
   ```bash
   cd pmcc-bot
   railway init
   # Select "Create new project"
   # Choose a name
   ```

3. **Add Environment Variables**

   Option A - Via CLI:
   ```bash
   railway variables set TRADIER_API_KEY="your_key"
   railway variables set TRADIER_BASE_URL="https://sandbox.tradier.com/v1"
   railway variables set TELEGRAM_BOT_TOKEN="your_token"
   railway variables set TELEGRAM_CHAT_ID="your_chat_id"
   ```

   Option B - Via Dashboard:
   ```bash
   railway open
   # Go to Variables tab
   # Add each variable manually
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Monitor**
   ```bash
   railway logs
   # Or use the web dashboard
   ```

6. **Database Persistence**
   - Railway automatically creates a persistent volume
   - Database survives restarts and redeployments
   - Located at `/app/pmcc.db` in the container

### Updating

```bash
# Make code changes locally
railway up  # Redeploys with new code
```

---

## 2. Render Deployment

**Pros**: Free tier, easy GitHub integration
**Cons**: Slower cold starts than Railway

### Steps:

1. **Create Account**
   - Go to [render.com](https://render.com)
   - Sign up (can use GitHub)

2. **Create New Service**
   - Click "New +" → "Background Worker"
   - Connect your GitHub repo or upload code

3. **Configure**
   - Name: `pmcc-bot`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`

4. **Add Environment Variables**
   - Go to "Environment" tab
   - Add each variable from `.env.example`

5. **Add Disk for Persistence**
   - Go to "Disks" tab
   - Add disk: `/opt/render/project/src/pmcc.db`
   - Size: 1GB (free tier)

6. **Deploy**
   - Click "Create Background Worker"
   - Wait for build and deployment

### Updating

- Push to GitHub → Auto-deploys (if connected)
- Or manually trigger deploy from Render dashboard

---

## 3. Linux VPS (DigitalOcean, Linode, AWS EC2)

**Pros**: Full control, predictable performance
**Cons**: Requires server management, costs money

### Prerequisites

- Ubuntu 20.04+ or Debian 11+
- Sudo access
- Public IP address

### Steps:

1. **SSH into Server**
   ```bash
   ssh user@your-server-ip
   ```

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv git
   ```

3. **Clone/Upload Code**
   ```bash
   cd ~
   git clone <your-repo>  # or upload via scp
   cd pmcc-bot
   ```

4. **Run Setup**
   ```bash
   ./setup.sh
   ```

5. **Configure Environment**
   ```bash
   nano .env
   # Add your API credentials
   ```

6. **Test**
   ```bash
   source venv/bin/activate
   python test_connection.py
   ```

7. **Create Systemd Service**
   ```bash
   # Edit service file with your paths
   sudo nano /etc/systemd/system/pmcc-bot.service
   ```

   Replace placeholders in `pmcc-bot.service`:
   - `your_username` → Your Linux username
   - `/path/to/pmcc-bot` → Full path (e.g., `/home/ubuntu/pmcc-bot`)

8. **Create Log Directory**
   ```bash
   sudo mkdir -p /var/log/pmcc-bot
   sudo chown $USER:$USER /var/log/pmcc-bot
   ```

9. **Enable and Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable pmcc-bot
   sudo systemctl start pmcc-bot
   ```

10. **Check Status**
    ```bash
    sudo systemctl status pmcc-bot
    sudo journalctl -u pmcc-bot -f
    ```

### Managing the Service

```bash
# Stop
sudo systemctl stop pmcc-bot

# Restart
sudo systemctl restart pmcc-bot

# View logs
sudo journalctl -u pmcc-bot -f

# Disable autostart
sudo systemctl disable pmcc-bot
```

### Updating Code

```bash
# Stop service
sudo systemctl stop pmcc-bot

# Update code
cd ~/pmcc-bot
git pull  # or upload new files

# Restart service
sudo systemctl start pmcc-bot
```

---

## 4. Docker Deployment

**Pros**: Portable, isolated, reproducible
**Cons**: Requires Docker knowledge

### Using Docker Compose (Recommended)

1. **Install Docker**
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

2. **Configure**
   ```bash
   cd pmcc-bot
   cp .env.example .env
   nano .env  # Add your credentials
   ```

3. **Build and Run**
   ```bash
   docker-compose up -d
   ```

4. **View Logs**
   ```bash
   docker-compose logs -f
   ```

5. **Stop**
   ```bash
   docker-compose down
   ```

### Using Docker Directly

```bash
# Build
docker build -t pmcc-bot .

# Run
docker run -d \
  --name pmcc-bot \
  --restart unless-stopped \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  pmcc-bot

# Logs
docker logs -f pmcc-bot

# Stop
docker stop pmcc-bot
docker rm pmcc-bot
```

### Database Persistence

The `data` directory is mounted as a volume. Database persists across container restarts.

---

## 5. Local Development

**Pros**: Easy debugging, no deployment needed
**Cons**: Requires keeping computer running

### Steps:

1. **Setup**
   ```bash
   ./setup.sh
   ```

2. **Configure**
   ```bash
   nano .env
   ```

3. **Test**
   ```bash
   source venv/bin/activate
   python test_connection.py
   ```

4. **Run**
   ```bash
   python main.py
   ```

### Keep Running in Background

**Option A - tmux**:
```bash
tmux new -s pmcc
source venv/bin/activate
python main.py
# Press Ctrl+B, then D to detach
# Reconnect: tmux attach -t pmcc
```

**Option B - screen**:
```bash
screen -S pmcc
source venv/bin/activate
python main.py
# Press Ctrl+A, then D to detach
# Reconnect: screen -r pmcc
```

**Option C - nohup**:
```bash
nohup python main.py > pmcc.log 2>&1 &
# View logs: tail -f pmcc.log
# Stop: ps aux | grep main.py, then kill <PID>
```

---

## Production Checklist

Before deploying for real trading:

- [ ] Switch to production Tradier API
  ```bash
  TRADIER_BASE_URL=https://api.tradier.com/v1
  ```

- [ ] Test all Telegram commands
  ```bash
  /positions, /alerts, /summary, /roll, /newcall, /close
  ```

- [ ] Verify alert thresholds match your strategy
  ```bash
  # Check config.py or .env
  ```

- [ ] Set up automatic backups
  ```bash
  # Cron job to backup pmcc.db daily
  0 2 * * * cp /path/to/pmcc.db /path/to/backups/pmcc-$(date +\%Y\%m\%d).db
  ```

- [ ] Enable monitoring/logging
  ```bash
  # Set LOG_LEVEL=INFO in production
  # Set LOG_LEVEL=DEBUG for troubleshooting
  ```

- [ ] Document your cost basis for taxes
  ```bash
  # Export data regularly
  sqlite3 pmcc.db ".dump" > backup.sql
  ```

- [ ] Test failure recovery
  ```bash
  # Stop bot, restart, verify positions intact
  ```

---

## Monitoring & Maintenance

### Health Checks

**Railway/Render**: Built-in monitoring dashboards

**VPS/Docker**: Set up simple monitoring
```bash
# Create healthcheck script
cat > healthcheck.sh << 'EOF'
#!/bin/bash
if ! pgrep -f "python main.py" > /dev/null; then
    echo "Bot not running!" | mail -s "PMCC Bot Alert" your@email.com
    sudo systemctl restart pmcc-bot
fi
EOF

chmod +x healthcheck.sh

# Add to crontab (check every 5 minutes)
*/5 * * * * /path/to/healthcheck.sh
```

### Log Rotation

**Systemd**: Automatic via journald

**Docker**: Configured in docker-compose.yml (10MB max, 3 files)

**Manual**:
```bash
# Add to /etc/logrotate.d/pmcc-bot
/var/log/pmcc-bot/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### Database Backups

**Automatic backup script**:
```bash
#!/bin/bash
# backup-db.sh
BACKUP_DIR="/path/to/backups"
DB_PATH="/path/to/pmcc.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_PATH "$BACKUP_DIR/pmcc-$DATE.db"

# Keep only last 30 days
find $BACKUP_DIR -name "pmcc-*.db" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup-db.sh
```

---

## Troubleshooting Deployments

### Railway

**Bot keeps restarting**:
- Check logs: `railway logs`
- Verify environment variables are set
- Check if database path is writable

**Can't connect to Tradier**:
- Verify API key in variables
- Check if Railway IP is blocked by Tradier

### Render

**Disk full error**:
- Increase disk size in settings
- Clean up old database backups

**Cold starts slow**:
- Normal on free tier
- Upgrade to paid tier for instant starts

### VPS/Systemd

**Service won't start**:
```bash
# Check status
sudo systemctl status pmcc-bot

# Check logs
sudo journalctl -u pmcc-bot -n 50

# Common issues:
# - Wrong paths in service file
# - Permission errors
# - Python venv not activated
```

**Database locked**:
```bash
# Check for multiple instances
ps aux | grep main.py
# Kill duplicates
```

### Docker

**Container exits immediately**:
```bash
# Check logs
docker logs pmcc-bot

# Run interactively for debugging
docker run -it --env-file .env pmcc-bot /bin/bash
```

**Database not persisting**:
```bash
# Verify volume mount
docker inspect pmcc-bot | grep Mounts -A 10
```

---

## Cost Comparison

| Platform | Free Tier | Paid Tier | Notes |
|----------|-----------|-----------|-------|
| Railway | 500 hrs/mo + $5 credit | $5-20/mo | Recommended |
| Render | 750 hrs/mo | $7/mo | Good alternative |
| DigitalOcean | None | $4/mo | Full control |
| AWS EC2 t2.micro | 750 hrs/mo (1st year) | $8/mo | Complex setup |
| Local | Free | Electricity | Must stay on 24/7 |

**Recommendation**: Start with Railway free tier, upgrade to paid if needed.

---

## Security Best Practices

1. **Never commit .env to Git**
   ```bash
   # Already in .gitignore
   ```

2. **Use read-only API keys where possible**
   - Tradier: No trading permissions needed
   - Telegram: Bot token should be kept secret

3. **Restrict server access**
   ```bash
   # VPS: Configure firewall
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

4. **Regular updates**
   ```bash
   # Update dependencies monthly
   pip install --upgrade -r requirements.txt
   ```

5. **Backup encryption**
   ```bash
   # Encrypt sensitive backups
   gpg -c pmcc.db
   ```

---

## Next Steps

After successful deployment:

1. Monitor for 24 hours
2. Verify alerts are triggering correctly
3. Test all Telegram commands
4. Add your real positions
5. Set up automated backups
6. Document your deployment for future reference

For issues, check the main [README.md](README.md) troubleshooting section.
