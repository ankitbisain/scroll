import sys
import webbrowser
from pathlib import Path
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from functools import partial
import json

from formatting.format_terminal import fit_to_screen

FORMAT = partial(fit_to_screen, margin=10, color="\033[47m\033[30m")
CATEGORIES = [f"math.{code}" for code in sys.argv[1:]]
DIR = Path(__file__).parent
TODAY = datetime.now(timezone.utc).date()


def load(date):
    try:
        with open(DIR / "papers" / f"{date}.json") as f:
            all = json.load(f)
        filtered = list(
            filter(lambda p: any(c in CATEGORIES for c in p.get("categories", [])), all)
        )
        tot = len(filtered)
        if tot:
            return [
                {**p, "index": i + 1, "tot": tot, "type": "paper"}
                for i, p in enumerate(filtered)
            ]
        return [{"type": "no_papers", "date": date.strftime("%m-%d")}]
    except FileNotFoundError:
        return [{"type": "no_papers", "date": date.strftime("%m-%d")}]


def display(paper):
    if paper["type"] == "no_papers":
        FORMAT([f"No papers found on {paper["date"]}"])
    else:
        header = f"{paper["date"]} ({paper["index"]}/{paper["tot"]})" + "\n"
        words = paper["abstract"].split()
        abstract = " ".join(words[:30]) + ("..." if words[30:] else "")
        FORMAT(
            [
                header,
                "\033[1m" + paper["title"] + "\033[22m",
                abstract,
            ]
        )


i = 0
papers = []
next_date = TODAY


def show():
    global i, papers, next_date
    if i >= len(papers):
        papers.extend(load(next_date))
        next_date = next_date - timedelta(days=1)
    display(papers[i])


while True:
    show()
    match input():
        case "m":
            if papers[i]["type"] == "paper":
                webbrowser.open(papers[i]["link"])
        case "z":
            i = max(0, i - 1)
        case _:
            i += 1
