import sqlite3
from config import DATABASE_FILE, DEFAULT_EXCHANGE_RATES

def init_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # 建立yt影片資料表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT PRIMARY KEY,
        video_url TEXT NOT NULL,
        title TEXT,
        channel TEXT,
        scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 建立超級感謝資料表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS super_thanks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT,
        currency TEXT NOT NULL,
        amount REAL NOT NULL,
        amount_twd REAL NOT NULL,
        commenter_name TEXT,
        comment_text TEXT,
        comment_date TIMESTAMP,
        scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos (video_id)
    )
    ''')
    
    # 建立貨幣匯率資料表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS currency_rates (
        currency TEXT PRIMARY KEY,
        rate_to_twd REAL NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 初始化貨幣匯率資料
    for currency, rate in DEFAULT_EXCHANGE_RATES.items():
        cursor.execute('''
        INSERT OR REPLACE INTO currency_rates (currency, rate_to_twd)
        VALUES (?, ?)
        ''', (currency, rate))
    
    conn.commit()
    return conn

def get_db_connection():
    return sqlite3.connect(DATABASE_FILE)