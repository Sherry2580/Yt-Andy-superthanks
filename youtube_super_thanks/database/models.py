class Video:
    def __init__(self, video_id, video_url, title=None, channel=None, scrape_date=None):
        self.video_id = video_id
        self.video_url = video_url
        self.title = title
        self.channel = channel
        self.scrape_date = scrape_date
    
    def to_dict(self):
        return {
            "video_id": self.video_id,
            "video_url": self.video_url,
            "title": self.title,
            "channel": self.channel,
            "scrape_date": self.scrape_date
        }

class SuperThanks: 
    def __init__(self, video_id, currency, amount, amount_twd, 
                 commenter_name=None, comment_text=None, comment_date=None, 
                 id=None, scrape_date=None):
        self.id = id
        self.video_id = video_id
        self.currency = currency
        self.amount = amount
        self.amount_twd = amount_twd
        self.commenter_name = commenter_name
        self.comment_text = comment_text
        self.comment_date = comment_date
        self.scrape_date = scrape_date
    
    def to_dict(self):
        return {
            "id": self.id,
            "video_id": self.video_id,
            "currency": self.currency,
            "amount": self.amount,
            "amount_twd": self.amount_twd,
            "commenter_name": self.commenter_name,
            "comment_text": self.comment_text,
            "comment_date": self.comment_date,
            "scrape_date": self.scrape_date
        }

class CurrencyRate:
    def __init__(self, currency, rate_to_twd, last_updated=None):
        self.currency = currency
        self.rate_to_twd = rate_to_twd
        self.last_updated = last_updated
    
    def to_dict(self):
        """轉換為字典"""
        return {
            "currency": self.currency,
            "rate_to_twd": self.rate_to_twd,
            "last_updated": self.last_updated
        }