from playwright.sync_api import sync_playwright
import re
from datetime import datetime
import os
from upload_to_sheets import upload_events_to_sheet
from export_to_csv import send_notification_email_with_attachment
from constants import (
    TITLE_KEYWORD_TO_CATEGORY,
    COMBINED_KEYWORD_TO_CATEGORY,
    UNWANTED_TITLE_KEYWORDS,
    FACEBOOK_LOCATION_MAP
)
from googleapiclient.http import MediaFileUpload

FB_PAGE_TO_CITY = {
    "facebook.com/VBParksRec": "Virginia Beach",
    "facebook.com/PortsmouthPublicLibrary": "Portsmouth",
    "facebook.com/HamptonVALib": "Hampton",
    "facebook.com/SuffolkPublicLibrary": "Suffolk",
    "facebook.com/NNLibrary": "Newport News",
    "facebook.com/NorfolkParksRec": "Norfolk",
    "facebook.com/ChesapeakePL": "Chesapeake",
}

def scrape_facebook_events(listing_url):
    print(f"🌐 Scraping event listings from: {listing_url}")
    city = next((val for key, val in FB_PAGE_TO_CITY.items() if key in listing_url), "Unknown")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(
            f"wss://production-sfo.browserless.io?token={os.environ['BROWSERLESS_TOKEN']}"
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        page.goto(listing_url, timeout=90000)

        print("📜 Scrolling page to load all content...")
        previous_height = 0
        for _ in range(50):
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                break
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(4000)
            previous_height = current_height
        print("✅ Finished scrolling.")

        # 🧼 Dismiss popup if visible
        try:
            popup_close = page.locator("div[aria-label='Close'], div[aria-label='Dismiss']").first
            if popup_close.is_visible():
                popup_close.click(timeout=3000)
                print("❎ Dismissed popup.")
        except:
            print("ℹ️ No popup found.")

        # 🔍 Save debug
        page.screenshot(path="facebook_debug.png", full_page=True)
        with open("facebook_debug.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        # 🧭 Find event links
        links = set()
        anchors = page.locator("a[href*='/events/']")
        count = anchors.count()
        print(f"🧪 Found {count} event anchors")

        for i in range(count):
            try:
                href = anchors.nth(i).get_attribute("href")
                if href and "/events/" in href and "/photos/" not in href:
                    full_link = href if href.startswith("http") else f"https://www.facebook.com{href}"
                    links.add(full_link)
            except:
                continue

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
                location = ""
                match = re.search(r"Location\s*([\w\s,]+)", raw_text)
                if match:
                    location = match.group(1).strip()
                elif "|" in title:
                    location = title.split("|")[-1].strip()

                desc_match = re.search(r"Details\s*(.*?)\n(?:Event by|Duration|Public)", raw_text, re.DOTALL | re.IGNORECASE)

                results.append({
                    "title": title.strip(),
                    "date": date_match.group(0) if date_match else "",
                    "city": city,
                    "start_time": time_match[0] if time_match else "",
                    "end_time": time_match[1] if len(time_match) > 1 else "",
                    "location": location,
                    "description": desc_match.group(1).strip() if desc_match else "",
                    "link": link
                })
            except Exception as e:
                print(f"⚠️ Failed to load {link} → {e}")
            finally:
                detail.close()

        browser.close()
        return results
