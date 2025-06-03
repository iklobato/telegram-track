from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import uuid
import threading
import os
from database.db_manager import DatabaseManager
from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.FLASK_SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*")

os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
db_manager = DatabaseManager(Config.DATABASE_PATH)

@app.route('/')
def dashboard():
    active_drivers = db_manager.get_active_drivers()
    return render_template('tracking.html', drivers=active_drivers)

@app.route('/generate-link')
def generate_link():
    driver_id = str(uuid.uuid4())
    tracking_link = Config.get_tracking_link(driver_id)
    
    db_manager.create_driver_session(driver_id)
    
    return jsonify({
        'driver_id': driver_id,
        'tracking_link': tracking_link,
        'instructions': 'Send this link to your driver. They need to click it and start sharing location.'
    })

@app.route('/api/driver-location/<driver_id>')
def get_driver_location(driver_id):
    location = db_manager.get_latest_location(driver_id)
    return jsonify(location)

@app.route('/api/all-drivers')
def get_all_drivers():
    drivers = db_manager.get_active_drivers_with_locations()
    return jsonify(drivers)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'driver-tracking-web',
        'database': 'connected' if db_manager else 'error'
    })

@socketio.on('connect')
def handle_connect():
    print('Client connected to dashboard')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from dashboard')

def broadcast_location_update(driver_id, location_data):
    socketio.emit('location_update', {
        'driver_id': driver_id,
        'location': location_data
    })

if __name__ == '__main__':
    print("🚚 Driver Tracking System - Web Server")
    print("=" * 50)
    
    if not Config.validate_config():
        print("\n❌ Configuration validation failed!")
        print("Please set the required environment variables.")
        exit(1)
    
    Config.print_config()
    
    if Config.is_production():
        print("\n🔒 Running in PRODUCTION mode")
        print("⚠️  Make sure to run the Telegram bot separately: python bot.py")
    else:
        print("\n🔧 Running in DEVELOPMENT mode")
        print("⚠️  Make sure to run the Telegram bot separately: python bot.py")
    
    print(f"🌐 Web server starting on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print("=" * 50)
    
    socketio.run(
        app, 
        debug=Config.FLASK_DEBUG, 
        host=Config.FLASK_HOST, 
        port=Config.FLASK_PORT,
        allow_unsafe_werkzeug=True
    ) 