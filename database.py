import sqlite3
import hashlib
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='stro.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create watchlist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, symbol)
            )
        ''')
        
        # Create alerts_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password):
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            return {'success': True, 'user_id': user_id}
        except sqlite3.IntegrityError as e:
            if 'username' in str(e):
                return {'success': False, 'error': 'Username already exists'}
            elif 'email' in str(e):
                return {'success': False, 'error': 'Email already registered'}
            else:
                return {'success': False, 'error': 'Registration failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, username, email FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'success': True,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2]
                }
            }
        else:
            return {'success': False, 'error': 'Invalid username or password'}
    
    def get_user_watchlist(self, user_id):
        """Get user's watchlist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol FROM watchlist
            WHERE user_id = ?
            ORDER BY added_at DESC
        ''', (user_id,))
        
        watchlist = cursor.fetchall()
        conn.close()
        
        return [item[0] for item in watchlist]
    
    def add_to_watchlist(self, user_id, symbol):
        """Add stock to user's watchlist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO watchlist (user_id, symbol)
                VALUES (?, ?)
            ''', (user_id, symbol))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Stock already in watchlist'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def remove_from_watchlist(self, user_id, symbol):
        """Remove stock from user's watchlist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM watchlist
            WHERE user_id = ? AND symbol = ?
        ''', (user_id, symbol))
        
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        return {'success': rows_affected > 0}
    
    def save_alert(self, user_id, symbol, alert_type, message):
        """Save alert to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts_history (user_id, symbol, alert_type, message)
            VALUES (?, ?, ?, ?)
        ''', (user_id, symbol, alert_type, message))
        
        conn.commit()
        conn.close()
    
    def get_user_alerts_history(self, user_id, limit=50):
        """Get user's alert history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, alert_type, message, created_at
            FROM alerts_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        alerts = cursor.fetchall()
        conn.close()
        
        return [{
            'symbol': alert[0],
            'alert_type': alert[1],
            'message': alert[2],
            'created_at': alert[3]
        } for alert in alerts]
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def add_alert(self, user_id, symbol, alert_type, message):
        """Add an alert to the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts_history (user_id, symbol, alert_type, message)
                VALUES (?, ?, ?, ?)
            ''', (user_id, symbol, alert_type, message))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_alerts(self, user_id, hours=None):
        """Get alerts for a user, optionally filtered by time"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if hours:
                time_threshold = datetime.now() - timedelta(hours=hours)
                cursor.execute('''
                    SELECT id, symbol, alert_type, message, created_at
                    FROM alerts_history
                    WHERE user_id = ? AND created_at > ?
                    ORDER BY created_at DESC
                ''', (user_id, time_threshold.isoformat()))
            else:
                cursor.execute('''
                    SELECT id, symbol, alert_type, message, created_at
                    FROM alerts_history
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 50
                ''', (user_id,))
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    'id': row[0],
                    'symbol': row[1],
                    'type': row[2],
                    'message': row[3],
                    'timestamp': row[4]
                })
            
            conn.close()
            return alerts
        except Exception as e:
            print(f"Error getting user alerts: {e}")
            return []
    
    def get_all_users(self):
        """Get all users in the system"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, username, email FROM users')
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'email': row[2]
                })
            
            conn.close()
            return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
