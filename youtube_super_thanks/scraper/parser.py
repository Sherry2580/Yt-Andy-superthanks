import re
from datetime import datetime
from collections import defaultdict

def parse_currency_amount(text):
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

def extract_video_id(video_url):
    if "youtube.com/watch?v=" in video_url:
        return video_url.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in video_url:
        return video_url.split("youtu.be/")[1].split("?")[0]
    else:
        return video_url

def print_currency_summary(conn, currency_totals, total_count, found_count):
    """按照貨幣分類並轉換為台幣"""
    from database.db_queries import get_currency_rate
    
    twd_total = 0
    twd_by_currency = {}
    
    print("\n=== TOTAL BY CURRENCY ===")
    for currency, total in sorted(currency_totals.items()):
        print(f"{currency} {total:.2f}")
        
        # 從資料庫獲取匯率
        rate = get_currency_rate(conn, currency)
        
        # 計算對應的台幣總額
        twd_amount = total * rate
        twd_by_currency[currency] = twd_amount
        twd_total += twd_amount
    
    print("\n=== CONVERTED TO TWD ===")
    for currency, twd_amount in sorted(twd_by_currency.items()):
        print(f"{currency} => TWD {twd_amount:.2f}")
    
    print("\n=== FINAL RESULTS ===")
    print(f"Total Comment Count: {found_count}")
    print(f"Total Super Thanks Count: {total_count}")
    print(f"Total (TWD): {twd_total:.1f} TWD")