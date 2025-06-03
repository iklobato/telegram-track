import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class DatabaseManager:
    def __init__(self, db_path: str = "database/tracking.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()

    def ensure_db_directory(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS drivers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    driver_id TEXT UNIQUE NOT NULL,
                    telegram_user_id INTEGER,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    driver_id TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (driver_id) REFERENCES drivers (driver_id)
                )
            """
            )

            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_driver_id ON locations (driver_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON locations (timestamp)"
            )

            conn.commit()

    def create_driver_session(self, driver_id: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO drivers (driver_id, is_active) VALUES (?, TRUE)",
                    (driver_id,),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating driver session: {e}")
            return False

    def register_driver(
        self, driver_id: str, telegram_user_id: int, username: str
    ) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE drivers 
                    SET telegram_user_id = ?, username = ?, is_active = TRUE 
                    WHERE driver_id = ?
                """,
                    (telegram_user_id, username, driver_id),
                )

                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                return False
        except Exception as e:
            print(f"Error registering driver: {e}")
            return False

    def store_location(self, driver_id: str, latitude: float, longitude: float) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO locations (driver_id, latitude, longitude)
                    VALUES (?, ?, ?)
                """,
                    (driver_id, latitude, longitude),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error storing location: {e}")
            return False

    def get_latest_location(self, driver_id: str) -> Optional[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT latitude, longitude, timestamp
                    FROM locations
                    WHERE driver_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """,
                    (driver_id,),
                )

                row = cursor.fetchone()
                if row:
                    return {
                        "latitude": row[0],
                        "longitude": row[1],
                        "timestamp": row[2],
                    }
                return None
        except Exception as e:
            print(f"Error getting latest location: {e}")
            return None

    def get_active_drivers(self) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT driver_id, username, created_at
                    FROM drivers
                    WHERE is_active = TRUE
                    ORDER BY created_at DESC
                """
                )

                rows = cursor.fetchall()
                return [
                    {
                        "driver_id": row[0],
                        "username": row[1] or "Unknown",
                        "created_at": row[2],
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"Error getting active drivers: {e}")
            return []

    def get_active_drivers_with_locations(self) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT d.driver_id, d.username, l.latitude, l.longitude, l.timestamp
                    FROM drivers d
                    LEFT JOIN (
                        SELECT driver_id, latitude, longitude, timestamp,
                               ROW_NUMBER() OVER (PARTITION BY driver_id ORDER BY timestamp DESC) as rn
                        FROM locations
                    ) l ON d.driver_id = l.driver_id AND l.rn = 1
                    WHERE d.is_active = TRUE
                    ORDER BY l.timestamp DESC
                """
                )

                rows = cursor.fetchall()
                return [
                    {
                        "driver_id": row[0],
                        "username": row[1] or "Unknown",
                        "latitude": row[2],
                        "longitude": row[3],
                        "last_update": row[4],
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"Error getting drivers with locations: {e}")
            return []

    def get_driver_by_user_id(self, telegram_user_id: int) -> Optional[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT driver_id, username
                    FROM drivers
                    WHERE telegram_user_id = ? AND is_active = TRUE
                """,
                    (telegram_user_id,),
                )

                row = cursor.fetchone()
                if row:
                    return {"driver_id": row[0], "username": row[1]}
                return None
        except Exception as e:
            print(f"Error getting driver by user ID: {e}")
            return None

    def deactivate_driver(self, driver_id: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE drivers 
                    SET is_active = FALSE 
                    WHERE driver_id = ?
                """,
                    (driver_id,),
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deactivating driver: {e}")
            return False
