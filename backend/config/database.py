import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME")
)

def get_db_connection():
    return connection_pool.getconn()

def release_db_connection(conn):
    connection_pool.putconn(conn)
    
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Initialize your database schema here
    try:
        # USERS TABLE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL,
                avatar VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
                ''')
        
        # CONVERSATIONS TABLE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(255) DEFAULT 'New Chat',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
                ''')
        
        # MESSAGES TABLE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
                sender VARCHAR(20) NOT NULL CHECK (sender IN ('user', 'bot')),
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
                ''')
        
        # INDEXES
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_conversation_user_id
            ON conversations(user_id)
            ''')
        
        cursor.execute('''
                       CREATE INDEX IF NOT EXISTS idx_message_conversation_id
                       ON messages(conversation_id)
                          ''')
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        cursor.close()
        release_db_connection(conn)