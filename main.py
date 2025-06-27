def scrape_facebook_events(page_url):
    print(f"🌐 Launching browser for: {page_url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        )
        page = context.new_page()
        page.goto(page_url, timeout=60000)
        page.wait_for_timeout(8000)  # wait for JS to load

        # ⬇️ Save the raw HTML *before* closing the browser
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        # Grab event titles
        event_titles = page.locator("div[role=article] h2").all_text_contents()

        print(f"✅ Found {len(event_titles)} event(s):")
        for title in event_titles:
            print("📅", title)

        browser.close()
