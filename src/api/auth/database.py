import sqlite3
from contextlib import contextmanager
import os
import logging

# Use test database if in test environment
DATABASE_URL = "test_auth.db" if os.getenv("TESTING") else "auth.db"

def init_db():
    """Initialize the database with the users and blacklisted_tokens tables"""
    with get_db() as db:
        cursor = db.cursor()
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                disabled BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Create blacklisted_tokens table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blacklisted_tokens (
                token TEXT PRIMARY KEY,
                blacklisted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    try:
        yield conn
    finally:
        conn.close()

def get_user(username: str):
    """Get user from database"""
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT username, email, hashed_password, full_name, disabled FROM users WHERE username=?", 
            (username,)
        )
        user = cursor.fetchone()
        if user:
            return dict(user)  # Convert Row to dict
        return None

def create_user(username: str, email: str, hashed_password: str):
    """Create new user in database"""
    try:
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
                (username, email, hashed_password)
            )
            db.commit()
            return True
    except sqlite3.IntegrityError:
        return False 

def blacklist_token(token: str) -> bool:
    """Add a token to the blacklist"""
    try:
        with get_db() as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO blacklisted_tokens (token) VALUES (?)",
                (token,)
            )
            db.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted"""
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT token FROM blacklisted_tokens WHERE token = ?",
            (token,)
        )
        return cursor.fetchone() is not None

def cleanup_blacklist():
    """Remove expired tokens from the blacklist"""
    try:
        with get_db() as db:
            cursor = db.cursor()
            # Remove tokens older than the maximum token lifetime
            cursor.execute("""
                DELETE FROM blacklisted_tokens 
                WHERE blacklisted_on < datetime('now', '-1 day')
            """)
            db.commit()
    except Exception as e:
        logging.error(f"Error cleaning up blacklist: {str(e)}")