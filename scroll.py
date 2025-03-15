from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
import time
from datetime import datetime
from collections import defaultdict

start_time = datetime.now()

def scrape_super_thanks(video_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-images")
    options.add_argument("--disable-extensions")
    options.page_load_strategy = 'eager'
    # options.add_argument("--headless=new")  # 無頭模式
    
    driver = webdriver.Chrome(options=options)
    
    currency_totals = defaultdict(float)
    total_count = 0
    
    try:
        driver.get(video_url)
        print(f"正在加載: {video_url}")
        
        time.sleep(5)
        
        scroll_to_load_comments(driver)
        wait = WebDriverWait(driver, 10)

        try:
            super_thanks_elements = driver.find_elements(By.CSS_SELECTOR, "#comment-chip-price")
            
            if super_thanks_elements:
                found_count = len(super_thanks_elements)
                print(f"找到 {len(super_thanks_elements)} 個評論")
                for i, element in enumerate(super_thanks_elements, 1):
                    amount_text = element.text.strip()
                    if amount_text:
                        print(f"超級感謝 #{i}: {amount_text}")
                        
                        # 解析不同貨幣金額
                        currency, amount = parse_currency_amount(amount_text)
                        if currency and amount:
                            currency_totals[currency] += amount
                            total_count += 1
                
                # 按貨幣分類並計算
                print_currency_summary(currency_totals, total_count, found_count)
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

def parse_currency_amount(text):
    """解析貨幣符號和金額"""
    currency_patterns = {
        'US$': r'US\$\s*([\d,.]+)',
        'CA$': r'CA\$\s*([\d,.]+)',  
        'HK$': r'HK\$\s*([\d,.]+)',  
        'SGD': r'SGD\s*([\d,.]+)',   
        'MYR': r'MYR\s*([\d,.]+)',   
        '¥': r'¥\s*([\d,.]+)',       
        'AU$': r'AU\$\s*([\d,.]+)',  
        '£': r'£\s*([\d,.]+)',       
        '€': r'€\s*([\d,.]+)',       
        'NZ$': r'NZ\$\s*([\d,.]+)',  
        'PHP': r'PHP\s*([\d,.]+)',   
        'THB': r'THB\s*([\d,.]+)',   
        'IDR': r'IDR\s*([\d,.]+)',   
        'TRY': r'TRY\s*([\d,.]+)',   
        'CLP': r'CLP\s*([\d,.]+)',   
        'ARS': r'ARS\s*([\d,.]+)',   
        'AED': r'AED\s*([\d,.]+)',   
        '$': r'^\$\s*([\d,.]+)',     
    }
    
    # 檢查各種貨幣格式
    for currency, pattern in currency_patterns.items():
        match = re.search(pattern, text)
        if match:
            return currency, float(match.group(1).replace(',', ''))
    
    # 如果無法辨識出格式，嘗試取出任何數字
    amount_match = re.search(r'[\d,.]+', text)
    if amount_match:
        currency_symbol = re.search(r'[^\d,.\s]+', text)
        if currency_symbol:
            return currency_symbol.group(0), float(amount_match.group(0).replace(',', ''))
    
    return None, None

def print_currency_summary(currency_totals, total_count, found_count):
    """按照貨幣分類並轉換為台幣"""
    exchange_rates = {
        '$': 1.0,           # 新台幣
        'US$': 32.95,       # 美元
        'HK$': 4.213,        # 港幣
        'SGD': 24.65,       # 新加坡元
        'CA$': 22.87,       # 加拿大元
        'MYR': 7.35,        # 馬來西亞令吉
        '¥': 0.22,          # 日元
        'AU$': 20.78,       # 澳元
        '£': 42.48,         # 英鎊
        '€': 35.7,         # 歐元
        'NZ$': 18.85,       # 紐西蘭元
        'PHP': 0.55,        # 菲律賓比索
        'THB': 0.96,        # 泰銖
        'IDR': 0.0020,      # 印尼盾
        'TRY': 0.97,        # 土耳其里拉
        'CLP': 0.035,       # 智利比索
        'ARS': 0.035,       # 阿根廷比索
        'AED': 8.59,        # 阿聯酋迪拉姆
    }
    
    twd_total = 0
    twd_by_currency = {}
    
    print("\n=== TOTAL BY CURRENCY ===")
    for currency, total in sorted(currency_totals.items()):
        print(f"{currency} {total:.2f}")
        
        # 計算對應的台幣總額
        if currency in exchange_rates:
            twd_amount = total * exchange_rates[currency]
            twd_by_currency[currency] = twd_amount
            twd_total += twd_amount
    
    print("\n=== CONVERTED TO TWD ===")
    for currency, twd_amount in sorted(twd_by_currency.items()):
        print(f"{currency} => TWD {twd_amount:.2f}")
    
    print("\n=== FINAL RESULTS ===")
    print(f"Total Comment Count: {found_count}")
    print(f"Total Super Thanks Count: {total_count}")
    print(f"Total (TWD): {twd_total:.1f} TWD")
    
    print("Script finished.")

def scroll_to_load_comments(driver, max_scrolls=100):  # 滾動次數
    """加載評論"""
    scroll_pause_time = 6  # 暫停時間
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    comments_count = 0
    no_change_count = 0
    
    print("comments loading...")
    
    for i in range(max_scrolls):
        try:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            current_comments = len(driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer"))
            
            # 如果找到更多評論，重置無變化計數器
            if current_comments > comments_count:
                if i % 50 == 0 or current_comments - comments_count > 10:
                    print(f"滾動 {i+1}/{max_scrolls} - 發現評論數: {current_comments} (+{current_comments - comments_count})")
                comments_count = current_comments
                no_change_count = 0
            else:
                no_change_count += 1
            
            # 如果頁面高度沒有變化且評論數也沒變化
            if new_height == last_height and no_change_count > 10:
                print(f"連續 {no_change_count} 次滾動沒有新評論")
                break
                
            last_height = new_height
            
        except Exception as e:
            print(f"scroll error: {str(e)}")
            time.sleep(5)
            continue
    
    print(f"Finish - 總共找到 {comments_count} 條評論")
    return comments_count

if __name__ == "__main__":
    video_input = input("輸入YouTube影片URL或ID: ")
    
    if "youtube.com" in video_input or "youtu.be" in video_input:
        video_url = video_input
    else:
        video_url = f"https://www.youtube.com/watch?v={video_input}"
    
    scrape_super_thanks(video_url)