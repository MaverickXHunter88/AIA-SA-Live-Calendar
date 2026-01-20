import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from ics import Calendar, Event

CALENDAR_URL = "https://aiasa.org/events-calendar/"


def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }

    r = requests.get(CALENDAR_URL, headers=headers, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    cal = Calendar()

    # Pull event links from the listing page
    event_links = soup.select("a[href*='/event/'], a[href*='?event=']")

    seen = set()

    for a in event_links:
        href = a.get("href")
        title = clean_text(a.get_text())

        if not href or not title:
            continue

        key = (href, title)
        if key in seen:
            continue
        seen.add(key)

        e = Event()
        e.name = title

        if href.startswith("http"):
            e.url = href
        else:
            e.url = f"https://aiasa.org{href}"

        # Placeholder time (we’ll upgrade later to real event times)
        e.begin = datetime.now(timezone.utc)

        cal.events.add(e)

    with open("events.ics", "w", encoding="utf-8") as f:
        f.writelines(cal.serialize_iter())

    print(f"Generated events.ics with {len(cal.events)} events")


if __name__ == "__main__":
    main()
