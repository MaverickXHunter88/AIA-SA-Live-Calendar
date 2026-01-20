import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from ics import Calendar, Event

CALENDAR_URL = "https://aiasa.org/events-calendar/"

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def main():
    r = requests.get(CALENDAR_URL, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    cal = Calendar()

    # Grab event links from the listing page
    # (We’ll improve the date/time parsing in the next upgrade)
    event_links = soup.select("a[href*='/event/'], a[href*='?event=']")

    seen = set()

    for a in event_links:
        href = a.get("href")
        title = clean_text(a.get_text())

        if not href or not title:
            continue

        # Avoid duplicates
        key = (href, title)
        if key in seen:
            continue
        seen.add(key)

        # Build the event
        e = Event()
        e.name = title

        if href.startswith("http"):
            e.url = href
        else:
            e.url = f"https://aiasa.org{href}"

        # Placeholder date (so the .ics stays valid)
        # Next step: parse real date/time from each event page.
        e.begin = datetime.now(timezone.utc)

        cal.events.add(e)

    with open("events.ics", "w", encoding="utf-8") as f:
        f.writelines(cal.serialize_iter())

    print(f"Generated events.ics with {len(cal.events)} events")

if __name__ == "__main__":
    main()
