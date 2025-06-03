# Real-Time Driver Tracking System

A production-ready server-side application for real-time driver location tracking using Flask, Telegram Bot, and WebSocket for live updates.

## Features

- 🚚 **Real-time tracking** with WebSocket updates
- 📱 **Telegram bot integration** for driver onboarding
- 🗺️ **Interactive web dashboard** with live driver locations
- 🔄 **Silent auto-tracking mode** (one-click activation)
- 📍 **Manual location sharing** for one-time updates
- 💾 **SQLite database** with persistent storage
- 📱 **Responsive design** for all devices
- 🔗 **Link generation** for easy driver registration
- 🐳 **Docker support** for easy deployment
- 🔒 **Production-ready** configuration

## Architecture

This is a **server-side application** designed to be deployed on a server and accessed by logistics managers through web browsers. The system consists of:

- **Web Server** (`app.py`) - Flask application with dashboard
- **Telegram Bot** (`bot.py`) - Handles driver interactions
- **Shared Database** - SQLite database for data persistence
- **Real-time Updates** - WebSocket communication for live tracking

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+ 
- Telegram Bot Token (from @BotFather)
- Virtual environment tool (uv, pip, or conda)

### 1. Setup Environment

```bash
# Clone repository
git clone <your-repository-url>
cd telegram-track

# Create virtual environment
uv venv  # or python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -r requirements.txt  # or pip install -r requirements.txt
```

### 2. Create Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` to create a new bot
3. Choose a name: `Your Company Driver Tracker`
4. Choose a username: `yourcompany_driver_bot`
5. Copy the bot token provided

### 3. Configure Environment Variables

```bash
# Required environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token_from_botfather"
export TELEGRAM_BOT_USERNAME="your_bot_username_without_@"
export FLASK_SECRET_KEY="your-secret-key-for-production"

# Local development specific
export DATABASE_PATH="database/tracking.db"  # Important: Use relative path for local dev
export FLASK_PORT="5001"  # Avoid port 5000 conflict with AirPlay on Mac
export FLASK_DEBUG="true"  # Enable debug mode for development
```

### 4. Start Services

**Terminal 1 - Web Server:**
```bash
cd telegram-track
source .venv/bin/activate
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_BOT_USERNAME="your_bot_username"
export DATABASE_PATH="database/tracking.db"
export FLASK_PORT="5001"
python app.py
```

**Terminal 2 - Telegram Bot:**
```bash
cd telegram-track
source .venv/bin/activate
export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_BOT_USERNAME="your_bot_username"
export DATABASE_PATH="database/tracking.db"
python bot.py
```

### 5. Access Dashboard

- Dashboard: http://localhost:5001
- Health check: http://localhost:5001/health

## Production Deployment

### Option 1: Docker Compose (Recommended)

1. **Setup environment:**
```bash
git clone <repository>
cd telegram-track
cp env.example .env
```

2. **Configure .env file:**
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_BOT_USERNAME=your_bot_username
FLASK_SECRET_KEY=your-production-secret-key-change-this
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
DATABASE_PATH=/app/data/tracking.db
```

3. **Deploy:**
```bash
docker-compose up -d
```

### Option 2: Manual Server Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_BOT_USERNAME="your_bot_username"
export FLASK_SECRET_KEY="your_secret_key"
export DATABASE_PATH="/var/lib/tracking/tracking.db"
export FLASK_DEBUG="false"

# Start web server (production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Start bot (separate terminal/service)
python bot.py
```

## Usage Guide

### For System Administrators:

1. **Deploy the server** using one of the methods above
2. **Verify both services are running:**
   - Check web server: `curl http://your-server:5000/health`
   - Check bot logs for "Application started"
3. **Share dashboard URL** with logistics managers

### For Logistics Managers:

1. **Access dashboard** at your server URL
2. **Generate tracking links:**
   - Click "Generate New Tracking Link" button
   - Copy the generated link
3. **Send links to drivers** via SMS, WhatsApp, or any messaging app
4. **Monitor real-time locations:**
   - Drivers appear in left sidebar when active
   - Click on driver names to center map view
   - Watch real-time updates as drivers move

### For Drivers:

1. **Click the tracking link** received from logistics coordinator
2. **Tracking starts automatically:**
   - No manual setup required
   - Simply click the link and share location once
   - System continues tracking silently in background
3. **Keep Telegram running** in background (can minimize the app)

## How It Works

### Silent Tracking Process:
1. **Manager generates link** → System creates unique driver ID
2. **Driver clicks link** → Telegram opens with bot
3. **Driver shares location once** → Tracking starts automatically
4. **Silent monitoring** → No further user interaction needed
5. **Real-time updates** → Managers see live location updates

### Link Format:
```
https://t.me/your_bot_username?start=[unique-driver-id]
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | - | ✅ |
| `TELEGRAM_BOT_USERNAME` | Bot username (without @) | - | ✅ |
| `FLASK_SECRET_KEY` | Flask session secret key | - | ✅ |
| `FLASK_HOST` | Server bind address | `0.0.0.0` | ❌ |
| `FLASK_PORT` | Server port | `5000` | ❌ |
| `FLASK_DEBUG` | Debug mode | `false` | ❌ |
| `DATABASE_PATH` | Database file path | `/app/data/tracking.db` | ❌ |
| `AUTO_TRACK_INTERVAL` | Auto-tracking interval (seconds) | `30` | ❌ |

## API Documentation

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard homepage |
| `/generate-link` | GET | Generate new driver tracking link |
| `/api/driver-location/<id>` | GET | Get specific driver's latest location |
| `/api/all-drivers` | GET | Get all active drivers with locations |
| `/health` | GET | Health check for load balancers |

### WebSocket Events

| Event | Direction | Data | Description |
|-------|-----------|------|-------------|
| `connect` | Client → Server | - | Client connects to dashboard |
| `disconnect` | Client → Server | - | Client disconnects |
| `location_update` | Server → Client | `{driver_id, location}` | Real-time location broadcast |

## Troubleshooting

### Common Issues

**❌ "Read-only file system: '/app'" Error:**
```bash
# Fix: Use relative path for local development
export DATABASE_PATH="database/tracking.db"
# Not: DATABASE_PATH="/app/data/tracking.db"
```

**❌ Bot not responding:**
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Ensure bot service is running: `python bot.py`
- Check bot logs for "Application started"

**❌ Web server won't start:**
- Port 5000 conflict (Mac AirPlay): Use `export FLASK_PORT=5001`
- Check if database directory exists
- Verify all environment variables are set

**❌ "AttributeError: 'Updater' object has no attribute":**
```bash
# Fix: Update telegram library
uv pip install python-telegram-bot==20.6
# or pip install python-telegram-bot==20.6
```

**❌ No real-time updates:**
- Ensure both web and bot services are running
- Check browser console for WebSocket errors
- Verify database is accessible by both services

### Health Checks

```bash
# Check web server
curl http://localhost:5001/health

# Expected response:
{
  "status": "healthy",
  "service": "driver-tracking-web", 
  "database": "connected"
}

# Check bot status
# Look for these log messages:
# "Application started"
# "HTTP Request: POST https://api.telegram.org/bot.../getMe"
```

### Log Monitoring

```bash
# Web server logs
tail -f app.log

# Bot logs  
tail -f bot.log

# Or run with verbose output:
python app.py  # Shows request logs
python bot.py  # Shows telegram API calls
```

## Deployment Examples

### Local Development Script
```bash
#!/bin/bash
# start-local.sh

export TELEGRAM_BOT_TOKEN="your_token_here"
export TELEGRAM_BOT_USERNAME="your_bot_username"  
export DATABASE_PATH="database/tracking.db"
export FLASK_PORT="5001"
export FLASK_DEBUG="true"

# Start web server in background
python app.py &
WEB_PID=$!

# Start bot
python bot.py &
BOT_PID=$!

echo "Services started:"
echo "Web server: http://localhost:5001 (PID: $WEB_PID)"
echo "Bot service PID: $BOT_PID"
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $WEB_PID $BOT_PID" EXIT
wait
```

### Systemd Service (Linux)
```ini
# /etc/systemd/system/driver-tracking-web.service
[Unit]
Description=Driver Tracking Web Server
After=network.target

[Service]
Type=simple
User=tracking
WorkingDirectory=/opt/driver-tracking
Environment=TELEGRAM_BOT_TOKEN=your_token_here
Environment=TELEGRAM_BOT_USERNAME=your_bot_username
Environment=DATABASE_PATH=/var/lib/tracking/tracking.db
ExecStart=/opt/driver-tracking/.venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Security Best Practices

- ✅ Use strong `FLASK_SECRET_KEY` in production
- ✅ Keep `TELEGRAM_BOT_TOKEN` secure and never commit to git
- ✅ Use HTTPS/SSL in production with reverse proxy
- ✅ Restrict database file permissions (600)
- ✅ Use firewall to limit access to necessary ports only
- ✅ Regular security updates for dependencies
- ✅ Monitor access logs for suspicious activity

## Performance Optimization

- **Single Server:** Handles 100+ concurrent drivers
- **Load Balancing:** Use Nginx/HAProxy for multiple instances  
- **Database:** Consider PostgreSQL for high-volume operations
- **Caching:** Redis for WebSocket scaling across instances
- **Monitoring:** Implement logging and metrics collection

## License

This project is production-ready and can be deployed for commercial use. 