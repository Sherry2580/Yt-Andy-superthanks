from datetime import datetime
from database.db_init import init_database
from database.db_queries import query_database
from scraper.scraper import scrape_super_thanks

def main_menu():
    while True:
        print("\n=== YouTube 超級感謝抓取工具 ===")
        print("1. 抓取新影片")
        print("2. 查詢資料庫")
        print("0. 退出")
        
        choice = input("請選擇操作 (0-2): ")
        
        if choice == "0":
            print("謝謝使用，再見!")
            break
        elif choice == "1":
            video_input = input("輸入YouTube影片URL或ID: ")
            
            if "youtube.com" in video_input or "youtu.be" in video_input:
                video_url = video_input
            else:
                video_url = f"https://www.youtube.com/watch?v={video_input}"
            
            # 開始抓取
            scrape_super_thanks(video_url)
        elif choice == "2":
            query_database()
        else:
            print("無效的選擇請重試")

if __name__ == "__main__":
    main_menu()