from playwright.sync_api import sync_playwright
import re
from datetime import date
import hashlib

def get_today_facebook_url():
    with open("facebook_pages.txt") as f:
        pages = [line.strip() for line in f if line.strip()]

    if not pages:
        raise Exception("No Facebook pages found in facebook_pages.txt")

    today = date.today().isoformat()
    idx = int(hashlib.md5(today.encode()).hexdigest(), 16) % len(pages)
    return pages[idx].replace("www.facebook.com", "m.facebook.com")

def scrape_facebook_events(listing_url):
    print(f"🌐 Scraping (mobile) event listings from: {listing_url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
            ),
            viewport={"width": 375, "height": 812}
        )
        page = context.new_page()
        page.goto(listing_url, timeout=60000)
        page.wait_for_timeout(5000)

        event_links = page.locator("a[href*='/events/']").element_handles()
        links = set()

        for el in event_links:
            href = el.get_attribute("href")
            if href and "/events/" in href:
                full_link = href if href.startswith("http") else f"https://m.facebook.com{href}"
                links.add(full_link)

        print(f"🔗 Found {len(links)} event links")

        results = []
        for link in links:
            print(f"➡️ Visiting: {link}")
            detail = context.new_page()
            try:
                detail.goto(link, timeout=60000)
                detail.wait_for_timeout(3000)

                title = detail.locator("h1, h2").first.text_content() or ""
                raw_text = detail.inner_text("body")

                date_match = re.search(r"\w+,\s+\w+\s+\d{1,2}", raw_text)
                time_match = re.findall(r"\d{1,2}:\d{2}\s[APMapm]{2}", raw_text)

                location_match = re.search(r"Location\s*([\w\s,]+)", raw_text)
                description_match = re.search(r"Details\s*([\s\S]+?)\n", raw_text)

                results.append({
                    "title": title.strip(),
                    "date": date_match.group(0) if date_match else "",
                    "start_time": time_match[0] if len(time_match) > 0 else "",
                    "end_time": time_match[1] if len(time_match) > 1 else "",
                    "location": location_match.group(1).strip() if location_match else "",
                    "description": (description_match.group(1).strip() if description_match else "").strip(),
                    "link": link
                })

            except Exception as e:
                print(f"⚠️ Error loading event: {link} → {e}")
            finally:
                detail.close()

        browser.close()

        print("\n✅ Final scraped events:")
        for event in results:
            print("📅", event)
