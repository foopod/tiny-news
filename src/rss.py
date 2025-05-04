import xmltodict
import requests
import json

class NewsType:
    LOCAL = "https://www.rnz.co.nz/rss/national.xml"
    WORLD = "https://www.rnz.co.nz/rss/world.xml"

def getRSS(url: str) -> dict:
    response = requests.get(url)
    return xmltodict.parse(response.content)
