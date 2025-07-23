from playwright.sync_api import sync_playwright
import re
from datetime import datetime
import hashlib
import os
from upload_to_sheets import upload_events_to_sheet
from constants import TITLE_KEYWORD_TO_CATEGORY  # make sure this is accessible

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
        previous_height = 0
        for _ in range(15):
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                break
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            previous_height = current_height
        print("✅ Finished scrolling.")

        links = set()
        for el in page.locator("a[href*='/events/']").element_handles():
            href = el.get_attribute("href")
            if href and "/events/" in href:
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

                # Parse date and time
                date_match = re.search(r"\w+,\s+\w+\s+\d{1,2}", raw_text)
                time_match = re.findall(r"\d{1,2}:\d{2}\s[APMapm]{2}", raw_text)

                location = ""
                match = re.search(r"Location\s*([\w\s,]+)", raw_text)
                if match:
                    location = match.group(1).strip()
                elif "|" in title:
                    location = title.split("|")[-1].strip()

                description_match = re.search(r"Details\s*([\s\S]+?)\n", raw_text)

                results.append({
                    "title": title.strip(),
                    "date": date_match.group(0) if date_match else "",
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


if __name__ == "__main__":
    try:
        all_scraped_events = []
        with open("facebook_pages.txt") as f:
            pages = [line.strip() for line in f if line.strip()]

        for url in pages:
            print(f"\n📄 Scraping from: {url}")
            events = scrape_facebook_events(url)
            all_scraped_events.extend(events)

        # ✅ Deduplicate by normalized link
        unique_events = {}
        for event in all_scraped_events:
            key = event["link"].split("?")[0]
            if key not in unique_events:
                unique_events[key] = event

        deduped_events = list(unique_events.values())

        for event in deduped_events:
            event["Event Name"] = event["title"] + " (Virginia Beach)"
            event["Event Link"] = event["link"]
            event["Event Status"] = "Available"
            event["Time"] = f"{event['start_time']} - {event['end_time']}"
            event["Ages"] = ""  # Facebook usually lacks this
            event["Location"] = event.get("location", "")
            event["Event Description"] = event.get("description", "")
            event["Series"] = ""

            # 🎯 Parse Month / Day / Year dynamically
            try:
                parsed_date = datetime.strptime(event["date"], "%A, %B %d")
                event["Month"] = parsed_date.strftime("%b")
                event["Day"] = str(parsed_date.day)
                event["Year"] = str(datetime.now().year)
            except:
                event["Month"] = ""
                event["Day"] = ""
                event["Year"] = str(datetime.now().year)

            # 🧠 Auto-assign categories based on keywords
            matched_categories = set()
            for keyword, category_string in TITLE_KEYWORD_TO_CATEGORY.items():
                if keyword.lower() in event["title"].lower():
                    matched_categories.update(c.strip() for c in category_string.split(","))
            event["Program Type"] = ", ".join(sorted(matched_categories))

        # ✅ Upload to Google Sheets
        upload_events_to_sheet(deduped_events, library="vbpl")

    except Exception as e:
        import traceback
        print("❌ Script failed:")
        traceback.print_exc()
