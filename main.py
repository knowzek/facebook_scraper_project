from playwright.sync_api import sync_playwright

def scrape_facebook_events(page_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        )
        page = context.new_page()
        page.goto(page_url, timeout=60000)
        page.wait_for_timeout(8000)  # Let content render

        event_titles = page.locator("div[role=article] h2").all_text_contents()
        browser.close()

        for title in event_titles:
            print("📅", title)

if __name__ == "__main__":
    scrape_facebook_events("https://www.facebook.com/VBParksRec/events")
