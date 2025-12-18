import arxiv
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone
from pathlib import Path


DIR = Path(__file__).parent
TODAY = datetime.now(timezone.utc).date()
URL = "https://arxiv.org/list/math/new"


def paper(result):
    return {
        "link": result.pdf_url,
        "categories": result.categories,
        "authors": [person.name for person in result.authors],
        "title": result.title,
        "abstract": result.summary,
        "date": TODAY.strftime("%m-%d"),
    }


def ids(url):
    # hardcoded dogshit to cut off crossposts and replacements
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    h3 = soup.find("h3", string=lambda t: t and "New submissions" in t)
    count = int(str(h3)[29:32])
    ids = [
        paper.find("a", title="Abstract")["href"].split("/")[-1]
        for paper in soup.find_all("dt")
    ]
    return ids[:count]


today_ids = ids(URL)

# check if website changed
new_id = str(today_ids[0])
with open(DIR / "papers" / "last.txt") as f:
    old_id = f.read()
if new_id != old_id:
    with open(DIR / "papers" / "last.txt", "w") as f:
        f.write(new_id)
    client = arxiv.Client()
    papers = []
    idlists = [today_ids[i : i + 100] for i in range(0, len(today_ids), 100)]
    for ids in idlists:
        search = arxiv.Search(id_list=ids)
        papers.extend([paper(result) for result in client.results(search)])
    with open(DIR / "papers" / f"{TODAY}.json", "w") as f:
        json.dump(papers, f, indent=2)
