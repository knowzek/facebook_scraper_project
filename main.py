from playwright.sync_api import sync_playwright
import re
from datetime import date
import hashlib
import os
import base64

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
        browser = p.chromium.connect_over_cdp(
            f"wss://production-sfo.browserless.io?token={os.environ['BROWSERLESS_TOKEN']}"
        )

        context = browser.contexts[0] if browser.contexts else browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        page.goto(listing_url, timeout=90000)
        print("📜 Scrolling page to load all content...")

        # Scroll slowly to trigger FB lazy loading
        for _ in range(15):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            page.wait_for_timeout(2000)

        print("✅ Finished scrolling.")
        page.screenshot(path="debug_fb_landing.png", full_page=True)
        print("📸 Screenshot saved.")

        # ⛏ Extract all event anchor links
        anchors = page.locator("a[href*='/events/']").element_handles()
        links = set()
        for el in anchors:
            href = el.get_attribute("href")
            if href and "/events/" in href and not href.endswith("/events"):  # filter the listing root itself
                full_link = href if href.startswith("http") else f"https://www.facebook.com{href}"
                links.add(full_link)

        print(f"🔗 Found {len(links)} event links.")

        results = []
        for link in links:
            print(f"➡️ Visiting event: {link}")
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
                    "start_time": time_match[0] if time_match else "",
                    "end_time": time_match[1] if len(time_match) > 1 else "",
                    "location": location_match.group(1).strip() if location_match else "",
                    "description": description_match.group(1).strip() if description_match else "",
                    "link": link
                })

            except Exception as e:
                print(f"⚠️ Failed to load: {link} → {e}")
            finally:
                detail.close()

        browser.close()
        print("✅ Final scraped events:")
        for r in results:
            print("📅", r)

if __name__ == "__main__":
    try:
        scrape_facebook_events(get_today_facebook_url())
    except Exception as e:
        import traceback
        print("❌ Script failed:")
        traceback.print_exc()
