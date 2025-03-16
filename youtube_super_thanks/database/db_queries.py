from datetime import datetime
from database.db_init import get_db_connection
from config import DATABASE_FILE

def save_video_info(conn, video_info):
    """儲存影片資訊到資料庫"""
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO videos (video_id, video_url, title, channel)
    VALUES (?, ?, ?, ?)
    ''', (
        video_info["video_id"],
        video_info["video_url"],
        video_info["title"],
        video_info["channel"]
    ))
    conn.commit()

def get_currency_rate(conn, currency):
    """從資料庫獲取貨幣匯率"""
    cursor = conn.cursor()
    cursor.execute('SELECT rate_to_twd FROM currency_rates WHERE currency = ?', (currency,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        # 如果找不到匯率，返回1.0作為默認值
        return 1.0

def save_super_thanks(conn, video_id, super_thanks_data):
    """儲存超級感謝資料到資料庫"""
    cursor = conn.cursor()
    
    for item in super_thanks_data:
        cursor.execute('''
        INSERT INTO super_thanks (
            video_id, currency, amount, amount_twd,
            commenter_name, comment_text, comment_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_id,
            item["currency"],
            item["amount"],
            item["amount_twd"],
            item.get("commenter_name", ""),
            item.get("comment_text", ""),
            item.get("comment_date", datetime.now())
        ))
    
    conn.commit()

def run_statistics(conn, video_id):
    cursor = conn.cursor()
    
    print("\n=== DATABASE STATISTICS ===")
    
    # 1. 查詢總共抓取的影片數量
    cursor.execute('SELECT COUNT(*) FROM videos')
    total_videos = cursor.fetchone()[0]
    print(f"資料庫中總影片數: {total_videos}")
    
    # 2. 查詢總共抓取的超級感謝數量
    cursor.execute('SELECT COUNT(*) FROM super_thanks')
    total_super_thanks = cursor.fetchone()[0]
    print(f"資料庫中總超級感謝數: {total_super_thanks}")
    
    # 3. 計算總台幣金額
    cursor.execute('SELECT SUM(amount_twd) FROM super_thanks')
    total_twd = cursor.fetchone()[0] or 0
    print(f"資料庫中總台幣金額: {total_twd:.1f} TWD")
    
    # 4. 計算本影片的統計資料
    cursor.execute('''
    SELECT COUNT(*), SUM(amount_twd) 
    FROM super_thanks 
    WHERE video_id = ?
    ''', (video_id,))
    result = cursor.fetchone()
    video_count = result[0] or 0
    video_twd = result[1] or 0
    
    print(f"本影片超級感謝數: {video_count}")
    print(f"本影片台幣總額: {video_twd:.1f} TWD")
    
    # 5. 計算最多超級感謝的影片
    cursor.execute('''
    SELECT v.title, COUNT(s.id) as count
    FROM videos v
    JOIN super_thanks s ON v.video_id = s.video_id
    GROUP BY v.video_id
    ORDER BY count DESC
    LIMIT 1
    ''')
    result = cursor.fetchone()
    if result:
        print(f"超級感謝最多的影片: {result[0]} ({result[1]}個)")
    
    # 6. 計算貢獻最多錢的影片
    cursor.execute('''
    SELECT v.title, SUM(s.amount_twd) as total
    FROM videos v
    JOIN super_thanks s ON v.video_id = s.video_id
    GROUP BY v.video_id
    ORDER BY total DESC
    LIMIT 1
    ''')
    result = cursor.fetchone()
    if result:
        print(f"貢獻最多錢的影片: {result[0]} ({result[1]:.1f} TWD)")

def query_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    while True:
        print("\n=== DATABASE QUERY MENU ===")
        print("1. 查詢所有影片")
        print("2. 查詢特定影片的超級感謝")
        print("3. 查詢貨幣匯率")
        print("4. 按貨幣統計超級感謝")
        print("0. 返回主選單")
        
        choice = input("請選擇操作 (0-4): ")
        
        if choice == "0":
            break
        elif choice == "1":
            cursor.execute('SELECT video_id, title, channel, scrape_date FROM videos')
            results = cursor.fetchall()
            print("\n=== 影片列表 ===")
            for row in results:
                print(f"ID: {row[0]}, 標題: {row[1]}, 頻道: {row[2]}, 抓取日期: {row[3]}")
        
        elif choice == "2":
            video_id = input("請輸入影片ID: ")
            cursor.execute('''
            SELECT currency, amount, amount_twd, commenter_name, comment_text, comment_date
            FROM super_thanks
            WHERE video_id = ?
            ''', (video_id,))
            results = cursor.fetchall()
            
            print(f"\n=== 影片 {video_id} 的超級感謝列表 ===")
            for row in results:
                print(f"{row[3]}: {row[0]} {row[1]:.2f} ({row[2]:.2f} TWD) - {row[4]}")
        
        elif choice == "3":
            cursor.execute('SELECT currency, rate_to_twd, last_updated FROM currency_rates')
            results = cursor.fetchall()
            print("\n=== 貨幣匯率列表 ===")
            for row in results:
                print(f"{row[0]}: {row[1]} TWD (更新於: {row[2]})")
        
        elif choice == "4":
            cursor.execute('''
            SELECT currency, COUNT(*) as count, SUM(amount) as total, SUM(amount_twd) as total_twd
            FROM super_thanks
            GROUP BY currency
            ORDER BY total_twd DESC
            ''')
            results = cursor.fetchall()
            print("\n=== 按貨幣統計超級感謝 ===")
            for row in results:
                print(f"{row[0]}: {row[1]}筆, 總額: {row[2]:.2f}, TWD總額: {row[3]:.2f}")
        
        else:
            print("無效的選擇，請重試")
    
    conn.close()