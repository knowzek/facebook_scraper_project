from playwright.sync_api import sync_playwright
import hashlib
from datetime import date

def get_today_facebook_url():
    with open("facebook_pages.txt") as f:
        pages = [line.strip() for line in f if line.strip()]

    if not pages:
        raise Exception("No Facebook pages found in facebook_pages.txt")

    today = date.today().isoformat()
    idx = int(hashlib.md5(today.encode()).hexdigest(), 16) % len(pages)
    return pages[idx]

def scrape_facebook_events(listing_url):
    print(f"🌐 Scraping event listings from: {listing_url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        )
        page = context.new_page()
        page.goto(listing_url, timeout=60000)
        page.wait_for_timeout(5000)

        # Step 1: Collect all event links from the page
        event_elements = page.locator('a[href*="/events/"]').element_handles()
        links = set()

        for el in event_elements:
            href = el.get_attribute("href")
            if href and "/events/" in href:
                full_link = href if href.startswith("http") else f"https://www.facebook.com{href}"
                links.add(full_link)

        print(f"🔗 Found {len(links)} event links")

        # Step 2: Visit each event page and scrape structured info
        results = []
        for link in links:
            print(f"➡️ Visiting: {link}")
            detail = context.new_page()
            try:
                detail.goto(link, timeout=60000)
                detail.wait_for_timeout(5000)

                title = detail.locator("h1").first.text_content() or ""
                time_block = detail.locator('[data-testid="event-permalink-details"]').inner_text() or ""
                location = detail.locator('[data-testid="event-permalink-details"] div:has-text("Location")').nth(1).text_content() or ""

                # Extract time parts with regex fallback
                import re
                times = re.findall(r"\d{1,2}:\d{2}\s[APM]{2}", time_block)
                start_time = times[0] if len(times) > 0 else ""
                end_time = times[1] if len(times) > 1 else ""

                date_match = re.search(r"\w+,\s+\w+\s+\d{1,2}", time_block)
                event_date = date_match.group(0) if date_match else ""

                results.append({
                    "title": title.strip(),
                    "date": event_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "location": location.strip(),
                    "link": link
                })

            except Exception as e:
                print(f"⚠️ Error loading event: {link} → {e}")
            finally:
                detail.close()

        browser.close()

        # Step 3: Print results
        print("\n✅ Final scraped events:")
        for event in results:
            print("📅", event)
