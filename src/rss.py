from http_utils import get_cached_rss


class NewsType:
    LOCAL = "Local"
    WORLD = "World"
    SCIENCE = "Science"
    TECH = "Tech"

    NewsMap = {
        "Local" : "https://www.rnz.co.nz/rss/national.xml",
        "World" : "https://feeds.bbci.co.uk/news/world/rss.xml",
        "Science" : "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "Tech" : "https://feeds.bbci.co.uk/news/technology/rss.xml"
    }

def getRSS(url: str) -> dict:
    return get_cached_rss(url)
