import os
from typing import Optional

class Config:
    """Configuration settings for the Driver Tracking System"""
    
    # Telegram Bot Configuration
    BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    BOT_USERNAME: str = os.getenv('TELEGRAM_BOT_USERNAME', '')
    
    # Flask Configuration
    FLASK_SECRET_KEY: str = os.getenv('FLASK_SECRET_KEY', 'change-this-in-production')
    FLASK_HOST: str = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT: int = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database Configuration
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', '/app/data/tracking.db')
    
    # Tracking Configuration
    AUTO_TRACK_INTERVAL: int = int(os.getenv('AUTO_TRACK_INTERVAL', 30))  # seconds
    MAX_GENERATED_LINKS: int = int(os.getenv('MAX_GENERATED_LINKS', 100))
    
    # Server Configuration
    ALLOWED_HOSTS: str = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is set"""
        missing_config = []
        
        if not cls.BOT_TOKEN:
            missing_config.append('TELEGRAM_BOT_TOKEN')
            
        if not cls.BOT_USERNAME:
            missing_config.append('TELEGRAM_BOT_USERNAME')
            
        if missing_config:
            print("❌ Missing required environment variables:")
            for item in missing_config:
                print(f"   - {item}")
            print("\n📚 Please set these environment variables before starting the server")
            return False
            
        return True
    
    @classmethod
    def get_tracking_link(cls, driver_id: str) -> str:
        """Generate tracking link for a driver"""
        return f"https://t.me/{cls.BOT_USERNAME}?start={driver_id}"
    
    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (for server logs)"""
        print("🔧 Server Configuration:")
        print(f"   Flask Host: {cls.FLASK_HOST}")
        print(f"   Flask Port: {cls.FLASK_PORT}")
        print(f"   Flask Debug: {cls.FLASK_DEBUG}")
        print(f"   Database: {cls.DATABASE_PATH}")
        print(f"   Bot Username: {cls.BOT_USERNAME}")
        print(f"   Auto Track Interval: {cls.AUTO_TRACK_INTERVAL}s")
        print(f"   Bot Token: {'✅ Set' if cls.BOT_TOKEN else '❌ Not Set'}")
        print(f"   Allowed Hosts: {cls.ALLOWED_HOSTS}")

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return not cls.FLASK_DEBUG

# Environment variables setup instructions
def setup_environment():
    """Print instructions for setting up environment variables"""
    print("""
🌍 Environment Variables Setup (Optional):

You can set these environment variables instead of editing the code:

export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_BOT_USERNAME="your_bot_username"
export FLASK_SECRET_KEY="your_secret_key_here"
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="5000"
export FLASK_DEBUG="False"
export DATABASE_PATH="database/tracking.db"
export AUTO_TRACK_INTERVAL="30"

Or create a .env file:
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=False
""")

if __name__ == '__main__':
    setup_environment()
    Config.print_config()
    Config.validate_config() 