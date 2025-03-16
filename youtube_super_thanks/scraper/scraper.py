import time
from datetime import datetime
from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import CSS_SELECTORS
from database.db_init import init_database
from database.db_queries import save_video_info, save_super_thanks, run_statistics, get_currency_rate
from scraper.browser import setup_browser, get_video_info, scroll_to_load_comments
from scraper.parser import extract_video_id, parse_currency_amount, print_currency_summary

def scrape_super_thanks(video_url):
    start_time = datetime.now()
    conn = init_database()
    
    driver = setup_browser()
    
    currency_totals = defaultdict(float)
    total_count = 0
    super_thanks_data = []
    
    try:
        driver.get(video_url)
        print(f"正在加載: {video_url}")
        
        time.sleep(5)
        
        video_id = extract_video_id(video_url)
        video_info = get_video_info(driver, video_id, video_url)
        save_video_info(conn, video_info)
        print(f"抓取影片: {video_info['title']} ({video_info['channel']})")
        
        # 滾動頁面加載評論
        scroll_to_load_comments(driver)
        wait = WebDriverWait(driver, 10)

        try:
            # 尋找超級感謝
            super_thanks_elements = driver.find_elements(By.CSS_SELECTOR, CSS_SELECTORS["super_thanks"])
            
            if super_thanks_elements:
                found_count = len(super_thanks_elements)
                
                # 尋找評論者名稱
                commenter_elements = []
                try:
                    commenter_elements = driver.find_elements(By.CSS_SELECTOR, CSS_SELECTORS["commenter_name"])
                except Exception as e:
                    print(f"獲取評論者名稱出錯: {str(e)}")
                
                # 獲取評論內容
                comment_text_elements = driver.find_elements(By.CSS_SELECTOR, CSS_SELECTORS["comment_text"])
                
                for i, element in enumerate(super_thanks_elements, 0):
                    amount_text = element.text.strip()
                    
                    if amount_text:
                        # 解析不同貨幣金額
                        currency, amount = parse_currency_amount(amount_text)
                        
                        if currency and amount:
                            rate = get_currency_rate(conn, currency)
                            amount_twd = amount * rate
                            
                            # 評論者名稱
                            commenter_name = ""
                            if i < len(commenter_elements):
                                try:
                                    raw_name = commenter_elements[i].text.strip()
                                    commenter_name = raw_name.split('@')[-1].strip() if '@' in raw_name else raw_name
                                except:
                                    commenter_name = f"未知評論者 #{i+1}"
                                
                                if not commenter_name:
                                    commenter_name = f"未知評論者 #{i+1}"
                            else:
                                commenter_name = f"未知評論者 #{i+1}"
                            
                            # 評論內容
                            comment_text = ""
                            if i < len(comment_text_elements):
                                comment_text = comment_text_elements[i].text.strip()
                            
                            print(f"超級感謝 #{i+1}: {currency} {amount:.2f} - 評論者: {commenter_name}")
                            
                            super_thanks_data.append({
                                "currency": currency,
                                "amount": amount,
                                "amount_twd": amount_twd,
                                "commenter_name": commenter_name,
                                "comment_text": comment_text,
                                "comment_date": datetime.now()
                            })
                            
                            # 累計總額
                            currency_totals[currency] += amount
                            total_count += 1
                
                # 保存超級感謝資料到資料庫
                save_super_thanks(conn, video_id, super_thanks_data)
                
                # 按貨幣分類並計算
                print_currency_summary(conn, currency_totals, total_count, found_count)
                
                # 執行統計分析
                run_statistics(conn, video_id)
            else:
                print("沒有找到超級感謝")
        
        except TimeoutException:
            print("time-out")
    
    except Exception as e:
        print(f"error: {str(e)}")
    
    finally:
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        print(f"耗時: {elapsed_time}")
        driver.quit()
        conn.close()