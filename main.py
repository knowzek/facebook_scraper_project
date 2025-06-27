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

def scrape_facebook_events(page_url):
    print(f"🌐 Launching browser for: {page_url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        )
        page = context.new_page()
        page.goto(page_url, timeout=60000)
        page.wait_for_selector('div[role="article"]', timeout=15000)

        # Save debug HTML for inspection
        print("\n🔍 DEBUG HTML (first 1000 chars):")
        print(page.content()[:1000])

        event_titles = page.locator("div[role=article] h2").all_text_contents()
        print(f"✅ Found {len(event_titles)} event(s):")
        for title in event_titles:
            print("📅", title)

        browser.close()

if __name__ == "__main__":
    url = get_today_facebook_url()
    print(f"📆 Scraping today’s URL: {url}")
    scrape_facebook_events(url)
