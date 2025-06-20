import xmltodict
import requests
import json

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
    response = requests.get(url)
    return xmltodict.parse(response.content)
