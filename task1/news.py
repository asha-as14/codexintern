import feedparser

class NewsClient:
    def __init__(self, rss_url=None):
        self.rss_url = rss_url or "https://news.google.com/rss"

    def get_headlines(self, limit=5):
        feed = feedparser.parse(self.rss_url)
        headlines = []
        for entry in feed.entries[:limit]:
            title = entry.title
            # optionally strip source prefix
            headlines.append(title)
        return headlines
