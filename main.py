from playwright.sync_api import sync_playwright
import re
from datetime import datetime
import hashlib
import os
from upload_to_sheets import upload_events_to_sheet
from export_to_csv import send_notification_email_with_attachment
import json

from constants import (
    TITLE_KEYWORD_TO_CATEGORY,
    COMBINED_KEYWORD_TO_CATEGORY,
    UNWANTED_TITLE_KEYWORDS,
    FACEBOOK_LOCATION_MAP
)

from googleapiclient.http import MediaFileUpload

def upload_debug_to_drive(service, filepath):
    file_metadata = {"name": os.path.basename(filepath)}
    media = MediaFileUpload(filepath, resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    print(f"📤 Uploaded debug file to Drive: {uploaded_file.get('id')}")

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
    city = "Unknown"
    for key, val in FB_PAGE_TO_CITY.items():
        if key in listing_url:
            city = val
            break

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
        previous_height = 0
        scroll_attempts = 0
        
        while scroll_attempts < 50:
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                break
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(4000)
            previous_height = current_height
            scroll_attempts += 1
        print("✅ Finished scrolling.")

        # 🔍 Save debug output
        page.screenshot(path="facebook_debug.png", full_page=True)
        html_content = page.content()
        if callable(html_content):
            html_content = html_content()
        
        with open("facebook_debug.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/drive.file']

        service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=credentials)
        
        upload_debug_to_drive(drive_service, "facebook_debug.html")
        upload_debug_to_drive(drive_service, "facebook_debug.png")

        raw_html = html_content

        # ✅ Extract event links by parsing raw HTML
        links = set()
        matches = re.findall(r'href="(\/events\/\d+[^\"]*)"', raw_html)
        
        for href in matches:

            if "/photos/" in href:
                continue
            full_link = href if href.startswith("http") else f"https://www.facebook.com{href}"
            links.add(full_link)

        print(f"🔗 Found {len(links)} event links.")
        for l in links:
            print("🔗 Link:", l)

        # ✅ Visit and extract data
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

                description_match = re.search(r"Details\s*(.*?)\n(?:Event by|Duration|Public)", raw_text, re.DOTALL | re.IGNORECASE)

                results.append({
                    "title": title.strip(),
                    "date": date_match.group(0) if date_match else "",
                    "city": city,
                    "start_time": time_match[0] if time_match else "",
                    "end_time": time_match[1] if len(time_match) > 1 else "",
                    "location": location,
                    "description": description_match.group(1).strip() if description_match else "",
                    "link": link
                })
            except Exception as e:
                print(f"⚠️ Failed to load: {link} → {e}")
            finally:
                detail.close()

        browser.close()
        return results

# === Main execution block ===
if __name__ == "__main__":
    try:
        all_scraped_events = []
        with open("facebook_pages.txt") as f:
            pages = [line.strip() for line in f if line.strip()]

        for url in pages:
            print(f"\n📄 Scraping from: {url}")
            events = scrape_facebook_events(url)
            all_scraped_events.extend(events)

        # Deduplicate
        unique_events = {}
        for event in all_scraped_events:
            key = event["link"].split("?")[0]
            if key not in unique_events:
                unique_events[key] = event
        deduped_events = list(unique_events.values())

        deduped_events = [
            e for e in deduped_events
            if not any(bad.lower() in e["title"].lower() for bad in UNWANTED_TITLE_KEYWORDS)
        ]

        # Enrich event metadata
        for event in deduped_events:
            city = event.get("city", "Unknown")
            raw_title = event.get("title", "")
            clean_title = raw_title.split("|")[0].strip() if "|" in raw_title else raw_title.strip()
            event["Event Name"] = clean_title if city.lower() in clean_title.lower() else f"{clean_title} ({city})"
            event["Event Link"] = event["link"]
            event["Event Status"] = "Available"
            event["Time"] = f"{event['start_time']} - {event['end_time']}"
            event["Ages"] = ""
            raw_location = event.get("location", "")
            mapped_location = FACEBOOK_LOCATION_MAP.get(raw_location.strip(), raw_location.strip())
            event["Location"] = mapped_location
            event["Event Description"] = event.get("description", "")
            event["Series"] = ""

            try:
                dt = datetime.strptime(event["date"], "%A, %B %d")
                event["Month"] = dt.strftime("%b")
                event["Day"] = str(dt.day)
                event["Year"] = str(datetime.now().year)
            except:
                event["Month"] = event["Day"] = ""
                event["Year"] = str(datetime.now().year)

            full_text = f"{event['title']} {event.get('description', '')}".lower()
            tags = []

            for keyword, cat in TITLE_KEYWORD_TO_CATEGORY.items():
                if keyword.lower() in full_text:
                    tags.extend([c.strip() for c in cat.split(",")])
            for (kw1, kw2), cat in COMBINED_KEYWORD_TO_CATEGORY.items():
                if kw1 in full_text and kw2 in full_text:
                    tags.extend([c.strip() for c in cat.split(",")])

            tags.append(f"Event Location - {city}")
            event["Categories"] = ", ".join(dict.fromkeys(tags))
            event["Program Type"] = event["Categories"]

        print(f"✅ Final event count: {len(deduped_events)}")
        for e in deduped_events:
            print(f"📅 {e['Event Name']} → {e['Event Link']}")

        upload_events_to_sheet(deduped_events, library="vbpl")

    except Exception as e:
        import traceback
        print("❌ Script failed:")
        traceback.print_exc()
        raise
