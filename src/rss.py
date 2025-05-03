import xmltodict
import requests
import json

def getRSS(url: str) -> dict:
    response = requests.get(url)
    return xmltodict.parse(response.content)

def saveRSS(filepath: str, data: dict) -> None:
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

data = getRSS("https://feeds.bbci.co.uk/news/technology/rss.xml")

saveRSS("database\\rss_feed_0.json", data)

# now read the news from the saved file
with open("database\\rss_feed_0.json", 'r') as file:
    data = json.load(file)
    
    for item in data['rss']['channel']['item']:
        print(item['title'])
        print(item['description'])
        print(item['link'])
        print()