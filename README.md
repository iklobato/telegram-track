# Real-Time Driver Tracking System

A production-ready server-side application for real-time driver location tracking using Flask, Telegram Bot, and WebSocket for live updates.

## Features

- 🚚 **Real-time tracking** with WebSocket updates
- 📱 **Telegram bot integration** for driver onboarding
- 🗺️ **Interactive web dashboard** with live driver locations
- 🔄 **Auto-tracking mode** (configurable interval via notifications)
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

## Quick Deployment

### Option 1: Docker Compose (Recommended)

1. **Clone and configure:**
```bash
git clone <repository>
cd telegram-track
cp env.example .env
# Edit .env with your bot credentials
```

2. **Set environment variables in .env:**
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_BOT_USERNAME=your_bot_username
FLASK_SECRET_KEY=your-production-secret-key
```

3. **Deploy:**
```bash
docker-compose up -d
```

4. **Access:**
- Dashboard: `http://your-server:5000`
- Health check: `http://your-server:5000/health`

### Option 2: Manual Server Deployment

1. **Setup environment:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_BOT_USERNAME="your_bot_username"
export FLASK_SECRET_KEY="your_secret_key"
export FLASK_DEBUG="false"
```

2. **Start services:**
```bash
# Terminal 1: Web server
python app.py

# Terminal 2: Telegram bot
python bot.py
```

3. **Production deployment with Gunicorn:**
```bash
# Web server
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Bot (separate process)
python bot.py
```

## Telegram Bot Setup

### 1. Create Bot with BotFather

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` to create a new bot
3. Choose a name: `Your Company Driver Tracker`
4. Choose a username: `yourcompany_driver_bot`
5. Copy the bot token provided

### 2. Configure Bot Settings

Send these commands to @BotFather:

```
/setcommands
start - Start driver tracking
stop - Stop tracking session

/setdescription
Real-time driver location tracking system for logistics management.

/setabouttext
Driver tracking bot for real-time location monitoring. Contact your logistics coordinator for tracking links.
```

## Server Configuration

### Environment Variables

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

### Production Considerations

- **Database**: For production, consider PostgreSQL with connection pooling
- **Web Server**: Use Nginx as reverse proxy with Gunicorn
- **Security**: Enable HTTPS/SSL with proper certificates
- **Monitoring**: Implement logging and monitoring solutions
- **Backup**: Regular database backups
- **Scaling**: Use Redis for WebSocket scaling across multiple instances

## Usage Guide

### For System Administrators:

1. **Deploy the server** using Docker or manual installation
2. **Configure environment variables** with bot credentials
3. **Set up monitoring** and backup procedures
4. **Share the dashboard URL** with logistics managers

### For Logistics Managers:

1. **Access dashboard** at your server URL
2. **Generate tracking links** for drivers
3. **Send links** to drivers via any communication method
4. **Monitor real-time** driver locations
5. **Click drivers** in sidebar to center map view

### For Drivers:

1. **Click tracking link** received from logistics
2. **Choose tracking mode:**
   - **📍 Share Location Once** - Manual updates
   - **🔄 Start Auto Tracking** - Automatic updates
3. **Keep Telegram running** for auto-tracking to work
4. **Respond to notifications** when prompted

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

## Monitoring & Maintenance

### Health Checks

```bash
# Check web server health
curl http://your-server:5000/health

# Expected response:
{
  "status": "healthy",
  "service": "driver-tracking-web",
  "database": "connected"
}
```

### Log Monitoring

- Web server logs: Check Flask/Gunicorn logs
- Bot logs: Monitor Python bot process logs
- Database: Monitor SQLite file size and locks

### Backup

```bash
# Backup database
cp /app/data/tracking.db /backup/tracking-$(date +%Y%m%d).db

# Automated backup script
*/6 * * * * cp /app/data/tracking.db /backup/tracking-$(date +\%Y\%m\%d-\%H\%M).db
```

## Scaling & Performance

### Single Server Setup
- Handles 100+ concurrent drivers
- Suitable for small to medium operations

### Multi-Server Setup
For larger operations, consider:
- **Load balancer** (Nginx/HAProxy)
- **PostgreSQL** database cluster
- **Redis** for WebSocket synchronization
- **Multiple app instances** behind load balancer

## Security

- ✅ Environment-based configuration
- ✅ No hardcoded secrets
- ✅ SQL injection prevention
- ✅ Input validation
- ✅ Health check endpoints
- ✅ Non-root Docker containers

Additional security measures:
- Enable HTTPS/SSL in production
- Use firewall to restrict access
- Regular security updates
- Monitor access logs

## Support & Troubleshooting

### Common Issues

**Bot not responding:**
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Ensure bot service is running
- Check bot logs for errors

**No real-time updates:**
- Verify WebSocket connection in browser console
- Check if both web and bot services are running
- Ensure database is accessible by both services

**Database errors:**
- Check database file permissions
- Verify `DATABASE_PATH` directory exists
- Monitor disk space

### Getting Help

1. Check server logs for error messages
2. Verify all environment variables are set
3. Test health endpoint: `/health`
4. Review Docker container logs if using Docker

## License

This project is production-ready and can be deployed for commercial use. 