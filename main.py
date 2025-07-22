from playwright.sync_api import sync_playwright
import re
from datetime import date
import hashlib
import base64

def get_today_facebook_url():
    print("🧪 Opening facebook_pages.txt...")
    with open("facebook_pages.txt") as f:
        pages = [line.strip() for line in f if line.strip()]

    if not pages:
        raise Exception("No Facebook pages found in facebook_pages.txt")

    today = date.today().isoformat()
    idx = int(hashlib.md5(today.encode()).hexdigest(), 16) % len(pages)
    return pages[idx]  # keep www.facebook.com

def scrape_facebook_events(listing_url):
    print(f"🌐 Scraping event listings from: {listing_url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            storage_state="auth.json"
        )

        page = context.new_page()
        page.goto(listing_url, timeout=60000)
        page.wait_for_timeout(5000)  # wait for page content to hydrate

        # 📸 Screenshot to debug
        page.screenshot(path="landing_page.png", full_page=True)
        print("📸 Screenshot saved: landing_page.png")
        with open("landing_page.png", "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            print("🖼️ Screenshot (base64):")
            print(encoded)

        # 📜 Scroll deeply to load events
        print("📜 Scrolling to load full page...")
        previous_height = 0
        for i in range(20):  # scroll up to 20 times
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                print("🛑 No more scrollable content detected.")
                break
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            previous_height = current_height
        print("✅ Finished scrolling.")


        # ⏳ Optional: wait again to let FB hydrate more
        page.wait_for_timeout(5000)

        # 🔗 Extract & filter real event links
        all_links = page.locator("a[href*='/events/']").element_handles()
        links = set()

        for el in all_links:
            href = el.get_attribute("href")
            if not href or "/events/" not in href:
                continue
            if any(x in href.lower() for x in ["create", "invite", "share", "#"]):
                continue
            full_link = href if href.startswith("http") else f"https://www.facebook.com{href}"
            links.add(full_link)

        print(f"🔗 Found {len(links)} event links")

        # 📅 Visit each event and extract details
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

if __name__ == "__main__":
    try:
        url = get_today_facebook_url()
        print(f"📆 Scraping today’s URL: {url}")
        scrape_facebook_events(url)
    except Exception as e:
        import traceback
        print("❌ Script failed:")
        traceback.print_exc()
