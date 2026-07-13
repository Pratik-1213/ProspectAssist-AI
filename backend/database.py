import sqlite3
import json
from contextlib import contextmanager

DB_NAME = "prospectassist.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table with role
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT DEFAULT 'loan_officer'
        )
    """)
    
    # Audit Logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_email TEXT,
            action TEXT,
            details TEXT
        )
    """)
    
    # Config table (for Rules Engine)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # Customers table (persisting leads)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            data JSON NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def log_audit(user_email: str, action: str, details: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (user_email, action, details) VALUES (?, ?, ?)",
        (user_email, action, details)
    )
    conn.commit()
    conn.close()

def save_customer(customer_id: str, customer_data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO customers (customer_id, data) VALUES (?, ?)",
        (customer_id, json.dumps(customer_data))
    )
    conn.commit()
    conn.close()

def get_all_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM customers")
    rows = cursor.fetchall()
    conn.close()
    return [json.loads(row['data']) for row in rows]

def get_customer(customer_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM customers WHERE customer_id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row['data']) if row else None

def get_config(key: str, default: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else default

def set_config(key: str, value: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()

# Initialize on import
init_db()
