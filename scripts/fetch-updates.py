"""Fetch news updates for each tracked park via Google News RSS.

Runs from GitHub Actions twice daily (7am + 7pm IST).
- Reads data/parks-index.json to know which parks to fetch.
- For each park id, looks up its query list in PARK_QUERIES.
- Writes data/updates/<id>.json (latest 10 items, deduped by URL).
- Items matching SIGNAL_PATTERNS get flagged for human review and
  copied into data/review-queue/<id>.json so maintainers can promote
  them into the curated timeline.
"""

import feedparser
import json
import os
import re
import urllib.parse
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))

# Add a new park id + queries here when expanding coverage.
PARK_QUERIES = {
    "kbr": [
        "KBR National Park Hyderabad",
        "KBR park tree felling",
        "H-CITI project Hyderabad",
        "Save KBR Hyderabad",
    ],
}

# Headlines matching any of these patterns are pulled out for human review.
SIGNAL_PATTERNS = [
    r"(\d{1,5})\s+trees?\s+(felled|cut|chopped|removed)",
    r"high\s+court.*?(stay|halt|order|judgment)",
    r"NGT.*?(order|stay|directive)",
    r"GO\s+(Ms|Rt)\.?\s*No\.?\s*\d+",
    r"new\s+commissioner",
    r"PCCF.*?(appointed|named)",
]


def fetch_query(q):
    url = (
        "https://news.google.com/rss/search?q="
        f"{urllib.parse.quote(q)}&hl=en-IN&gl=IN&ceid=IN:en"
    )
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:15]:
        items.append({
            "date": entry.get("published", ""),
            "headline": entry.title,
            "source": entry.get("source", {}).get("title", "") or "Google News",
            "url": entry.link,
        })
    return items


def detect_signals(text):
    return [p for p in SIGNAL_PATTERNS if re.search(p, text, re.IGNORECASE)]


def run_for_park(park_id, queries):
    seen, items, review = set(), [], []
    for q in queries:
        for item in fetch_query(q):
            if item["url"] in seen:
                continue
            seen.add(item["url"])
            flags = detect_signals(item["headline"])
            if flags:
                review.append({**item, "flags": flags})
                item["needsHumanReview"] = True
            items.append(item)

    items.sort(key=lambda x: x["date"], reverse=True)
    items = items[:10]

    os.makedirs("data/updates", exist_ok=True)
    with open(f"data/updates/{park_id}.json", "w", encoding="utf-8") as f:
        json.dump({
            "lastChecked": datetime.now(IST).isoformat(),
            "lastCheckSource": "GitHub Actions scheduled run",
            "items": items,
        }, f, indent=2, ensure_ascii=False)

    if review:
        os.makedirs("data/review-queue", exist_ok=True)
        with open(f"data/review-queue/{park_id}.json", "w", encoding="utf-8") as f:
            json.dump({
                "generated": datetime.now(IST).isoformat(),
                "items": review,
            }, f, indent=2, ensure_ascii=False)
        print(f"⚠ [{park_id}] {len(review)} items flagged for review")
    print(f"✓ [{park_id}] {len(items)} items written")


def main():
    with open("data/parks-index.json") as f:
        idx = json.load(f)
    for park in idx["parks"]:
        queries = PARK_QUERIES.get(park["id"], [park["name"]])
        run_for_park(park["id"], queries)


if __name__ == "__main__":
    main()
