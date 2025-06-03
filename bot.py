import logging
import asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from database.db_manager import DatabaseManager
from app import broadcast_location_update
from config import Config
import threading
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Ensure data directory exists
os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
db_manager = DatabaseManager(Config.DATABASE_PATH)

tracking_jobs = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    
    if args:
        driver_id = args[0]
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name
        
        if db_manager.register_driver(driver_id, user_id, username):
            # Check if already tracking
            if user_id in tracking_jobs:
                return  # Silent - no message if already tracking
            
            # No confirmation message - completely silent
            # Start silent background tracking immediately
            tracking_jobs[user_id] = True
            asyncio.create_task(silent_background_tracking(context.application, user_id, driver_id))
            
        else:
            # No error message - keep completely silent
            pass
    else:
        # No welcome message - keep completely silent
        pass

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    location = update.message.location
    user_id = update.effective_user.id
    
    driver_info = db_manager.get_driver_by_user_id(user_id)
    
    if driver_info:
        driver_id = driver_info['driver_id']
        
        location_data = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timestamp': update.message.date.isoformat()
        }
        
        # Store location silently
        if db_manager.store_location(driver_id, location.latitude, location.longitude):
            # Broadcast to dashboard without notifying driver
            threading.Thread(
                target=broadcast_location_update,
                args=(driver_id, location_data)
            ).start()
            # No confirmation message - completely silent
        # No error messages either - keep it silent
    # No "not registered" message - keep silent for unregistered users too

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = update.effective_user.id
    
    driver_info = db_manager.get_driver_by_user_id(user_id)
    
    if not driver_info:
        await update.message.reply_text("❌ You're not registered as a driver.")
        return
    
    driver_id = driver_info['driver_id']
    
    if text == "🔄 Start Auto Tracking":
        if user_id in tracking_jobs:
            await update.message.reply_text("⚠️ Auto tracking is already running!")
            return
        
        keyboard = [[KeyboardButton("🛑 Stop Auto Tracking")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        tracking_jobs[user_id] = True
        
        await update.message.reply_text(
            f"🔄 Auto tracking started!\n\n"
            f"📍 I'll request your location every {Config.AUTO_TRACK_INTERVAL} seconds\n"
            f"⚠️ Keep Telegram notifications ON\n"
            f"⚠️ Don't completely close Telegram\n\n"
            f"You can minimize the app, but keep it running in background.",
            reply_markup=reply_markup
        )
        
        asyncio.create_task(auto_track_location(context.application, user_id, driver_id))
        
    elif text == "🛑 Stop Auto Tracking":
        if user_id in tracking_jobs:
            tracking_jobs[user_id] = False
            del tracking_jobs[user_id]
            
            keyboard = [
                [KeyboardButton("📍 Share Location Once", request_location=True)],
                [KeyboardButton("🔄 Start Auto Tracking")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "🛑 Auto tracking stopped!",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("⚠️ Auto tracking is not running!")

async def silent_background_tracking(application, user_id, driver_id):
    """Completely silent background tracking - minimal location request only"""
    # Send only location sharing button without any text
    try:
        keyboard = [[KeyboardButton("📍", request_location=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await application.bot.send_message(
            chat_id=user_id,
            text="📍",  # Minimal text - just an emoji
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Error starting tracking for user {user_id}: {e}")
        if user_id in tracking_jobs:
            del tracking_jobs[user_id]

async def auto_track_location(application, user_id, driver_id):
    # Keep original function for manual tracking if needed
    while user_id in tracking_jobs and tracking_jobs[user_id]:
        try:
            keyboard = [[InlineKeyboardButton("📍 Send Location", callback_data=f"loc_{driver_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await application.bot.send_message(
                chat_id=user_id,
                text="📍 Please share your current location:",
                reply_markup=reply_markup
            )
            
            await asyncio.sleep(Config.AUTO_TRACK_INTERVAL)
            
        except Exception as e:
            logging.error(f"Error in auto tracking for user {user_id}: {e}")
            if user_id in tracking_jobs:
                del tracking_jobs[user_id]
            break

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("loc_"):
        driver_id = query.data.split("_")[1]
        user_id = query.from_user.id
        
        keyboard = [[KeyboardButton("📍", request_location=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        # Completely silent - no messages
        try:
            await query.edit_message_text("📍", reply_markup=None)
            # Don't send any additional message
        except Exception:
            # Ignore all errors - keep completely silent
            pass

async def stop_tracking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    driver_info = db_manager.get_driver_by_user_id(user_id)
    
    if driver_info:
        if db_manager.deactivate_driver(driver_info['driver_id']):
            await update.message.reply_text(
                "🛑 Tracking stopped. Thank you for using Driver Tracking!",
                reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True)
            )
        else:
            await update.message.reply_text("❌ Failed to stop tracking.")
    else:
        await update.message.reply_text("❌ You're not currently being tracked.")

def main():
    print("🤖 Driver Tracking System - Telegram Bot Server")
    print("=" * 60)
    
    if not Config.validate_config():
        print("\n❌ Configuration validation failed!")
        print("Please set the required environment variables.")
        exit(1)
    
    Config.print_config()
    
    if Config.is_production():
        print("\n🔒 Running in PRODUCTION mode")
    else:
        print("\n🔧 Running in DEVELOPMENT mode")
    
    print(f"\n📱 Bot will track location every {Config.AUTO_TRACK_INTERVAL} seconds in auto mode")
    print("🌐 Make sure the web server is running: python app.py")
    print("=" * 60)
    
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop_tracking))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🤖 Telegram bot server starting...")
    application.run_polling()

if __name__ == '__main__':
    main() 