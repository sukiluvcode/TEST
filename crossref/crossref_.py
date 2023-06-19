import requests
import json
import time
from decorator_ import Counts

BASE_URL = "https://api.crossref.org/members/316/works"

@Counts
def make_request(cursor="*"):
    headers ={
        "X-Rate-Limit-Limit": '50',
        "X-Rate-Limit-Interval": "1s"
    }
    params = {
        "query": "nonlinear optical crystals nlo inorganic",
        "filter": "type:journal-article,from-pub-date:2015",
        "select": "DOI,title",
        "cursor": cursor
    }

    res = requests.get(BASE_URL, params=params).json()
    length = collect_info(res)
    next_cursor = res["message"]["next-cursor"]
    return next_cursor, length

records = []
def collect_info(content):
    items = content["message"]["items"]
    records.extend(items)
    length = len(items)
    return length

next_cursor, length = make_request()
print(make_request.count)
while True:
        time.sleep(0.1)
        next_cursor, length = make_request(cursor=next_cursor)
        print(make_request.count)
        if length < 20:
            break

with open("crossref_nlo_doi.json", "w") as fo:
    fo.write(json.dumps(records, indent=4))
# 1337 requests 