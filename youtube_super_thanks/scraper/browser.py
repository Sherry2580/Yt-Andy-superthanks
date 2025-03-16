import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import BROWSER_SETTINGS, SCROLL_SETTINGS, CSS_SELECTORS

def setup_browser():
    """瀏覽器選項設置"""
    options = webdriver.ChromeOptions()
    
    if BROWSER_SETTINGS["disable_notifications"]:
        options.add_argument("--disable-notifications")
    
    if BROWSER_SETTINGS["disable_images"]:
        options.add_argument("--disable-images")
    
    if BROWSER_SETTINGS["disable_extensions"]:
        options.add_argument("--disable-extensions")
    
    options.page_load_strategy = BROWSER_SETTINGS["page_load_strategy"]
    
    if BROWSER_SETTINGS["headless"]:
        options.add_argument("--headless=new")
    
    return webdriver.Chrome(options=options)

def get_video_info(driver, video_id, video_url):
    """取影片標題和頻道名稱"""
    try:
        # 等待頁面加載
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, CSS_SELECTORS["video_title"]))
        )
        
        # 抓影片標題
        title_element = driver.find_element(By.CSS_SELECTOR, CSS_SELECTORS["video_title"])
        title = title_element.get_attribute("title") or title_element.text
        
        if not title:
            # 嘗試另一種方式獲取標題
            title_elements = driver.find_elements(By.CSS_SELECTOR, "h1.title yt-formatted-string")
            if title_elements:
                title = title_elements[0].text
        
        # 抓頻道名稱
        channel_element = driver.find_element(By.CSS_SELECTOR, CSS_SELECTORS["channel_name"])
        channel = channel_element.text if channel_element else "未知頻道"
        
        print(f"頻道: {channel}")
        print(f"影片資訊 - 標題: {title}, 頻道: {channel}")
        
        return {
            "video_id": video_id,
            "video_url": video_url,
            "title": title,
            "channel": channel
        }
    except Exception as e:
        print(f"error: {str(e)}")
        return {
            "video_id": video_id,
            "video_url": video_url,
            "title": "沒找到",
            "channel": "沒找到"
        }

def scroll_to_load_comments(driver, max_scrolls=None):
    """加載評論"""
    if max_scrolls is None:
        max_scrolls = SCROLL_SETTINGS["max_scrolls"]
    
    scroll_pause_time = SCROLL_SETTINGS["scroll_pause_time"]
    no_change_threshold = SCROLL_SETTINGS["no_change_threshold"]
    
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    comments_count = 0
    no_change_count = 0
    
    print("comments loading...")
    
    for i in range(max_scrolls):
        try:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            current_comments = len(driver.find_elements(By.CSS_SELECTOR, CSS_SELECTORS["comments"]))
            
            # 如果找到更多評論，重置無變化計數器
            if current_comments > comments_count:
                if i % 50 == 0 or current_comments - comments_count > 10:
                    print(f"滾動 {i+1}/{max_scrolls} - 發現評論數: {current_comments} (+{current_comments - comments_count})")
                comments_count = current_comments
                no_change_count = 0
            else:
                no_change_count += 1
            
            # 如果頁面高度沒有變化且評論數也沒變化
            if new_height == last_height and no_change_count > no_change_threshold:
                print(f"連續 {no_change_count} 次滾動沒有新評論")
                break
                
            last_height = new_height
            
        except Exception as e:
            print(f"scroll error: {str(e)}")
            time.sleep(5)
            continue
    
    print(f"Finish - 總共找到 {comments_count} 條評論")
    return comments_count