from datetime import datetime
import os
import gspread
from google.oauth2 import service_account
import traceback
from config import get_library_config
import json
import re
from constants import LIBRARY_CONSTANTS, TITLE_KEYWORD_TO_CATEGORY
from constants import COMBINED_KEYWORD_TO_CATEGORY

def _clean_link(url: str) -> str:
    cleaned = (
        url.replace("/index.php/", "/")
           .replace("/index.php", "/")
    )
    return cleaned.replace("://", ":::").replace("//", "/").replace(":::", "://")


def connect_to_sheet(spreadsheet_name, worksheet_name):
    creds = service_account.Credentials.from_service_account_file(
        "/etc/secrets/GOOGLE_APPLICATION_CREDENTIALS_JSON",
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    return client.open(spreadsheet_name).worksheet(worksheet_name)


def normalize(row):
    return [cell.strip() for cell in row[:13]] + [""] * (13 - len(row))


def upload_events_to_sheet(events, sheet=None, mode="full", library="vbpl", age_to_categories={}, name_suffix_map={}):
    config = get_library_config(library)
    SPREADSHEET_NAME = config["spreadsheet_name"]
    WORKSHEET_NAME = config["worksheet_name"]
    LOG_WORKSHEET_NAME = config["log_worksheet_name"]
    library_constants = LIBRARY_CONSTANTS.get(library, {})
    program_type_to_categories = library_constants.get("program_type_to_categories", {})


    PROGRAM_TYPE_TO_CATEGORIES = {
        "Storytimes & Early Learning": f"Event Location - {config['organizer_name']}, Audience - Free Event, Audience - Family Event, List - Storytimes",
        "STEAM": f"Event Location - {config['organizer_name']}, List - STEM/STEAM, Audience - Free Event, Audience - Family Event",
        "Computers & Technology": f"Event Location - {config['organizer_name']}, Audience - Free Event, Audience - Teens, Audience - Family Event",
        "Workshops & Lectures": f"Event Location - {config['organizer_name']}, Audience - Free Event, Audience - Family Event",
        "Discussion Groups": f"Event Location - {config['organizer_name']}, Audience - Free Event, Audience - Family Event",
        "Arts & Crafts": f"Event Location - {config['organizer_name']}, Audience - Free Event, Audience - Family Event",
        "Hobbies": f"Event Location - {config['organizer_name']}, Audience - Free Event, Audience - Family Event",
        "Books & Authors": f"Event Location - {config['organizer_name']}, Audience - Free Event, Audience - Family Event",
        "Culture": f"Event Location - {config['organizer_name']}, Audience - Free Event, Audience - Family Event",
        "History & Genealogy": f"Event Location - {config['organizer_name']}, Audience - Teens, Audience - Free Event"
    }

    try:
        if sheet is None:
            sheet = connect_to_sheet(SPREADSHEET_NAME, WORKSHEET_NAME)

        rows = sheet.get_all_values()
        headers = rows[0]
        existing_rows = rows[1:]

        for i, row in enumerate(existing_rows):
            if len(row) < 16:
                print(f"[WARN] Row {i + 2} too short: {len(row)} cols → {row}")
                row += [""] * (16 - len(row))

        link_to_row_index = {}
        existing_data = {}

        for idx, row in enumerate(existing_rows):
            if len(row) <= 1:
                continue
            clean_link = _clean_link(row[1].strip())
            link_to_row_index[clean_link] = idx + 2
            existing_data[clean_link] = row

        added = 0
        updated = 0
        skipped = 0

        new_rows = []
        update_requests = []

        for event in events:
            try:
                raw_link = (event.get("Event Link", "") or "").strip()
                if not raw_link:
                    print(f"⚠️  Skipping malformed event (missing link): {event.get('Event Name','')}")
                    skipped += 1
                    continue

                link = _clean_link(raw_link)

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                program_type = event.get("Program Type", "")

                if library == "ppl":
                    # Use pre-tagged categories or fallback from scraper
                    categories = event.get("Categories", "").strip()
                    if not categories:
                        categories = "Audience - Family Event, Audience - Free Event, Audience - Preschool Age, Audience - School Age, Event Location - Portsmouth"
                
                elif library == "hpl":
                    program_types = [pt.strip().lower() for pt in program_type.split(",") if pt.strip()]
                    matched_tags = []
                    for pt in program_types:
                        cat = program_type_to_categories.get(pt)
                        if cat:
                            matched_tags.extend([c.strip() for c in cat.split(",")])
                    categories = ", ".join(dict.fromkeys(matched_tags))  # remove duplicates, preserve order
                
                else:
                    # Default case for vbpl, npl, chpl, etc.
                    categories = program_type_to_categories.get(program_type, "")

                if library == "chpl" and age_to_categories:
                    audience_keys = [a.strip() for a in event.get("Ages", "").split(",") if a.strip()]
                    all_tags = []
                    for tag in audience_keys:
                        tags = age_to_categories.get(tag)
                        if tags:
                            all_tags.extend([t.strip() for t in tags.split(",")])
                    if all_tags:
                        categories = ", ".join(dict.fromkeys(all_tags))

                ages_raw = event.get("Ages", "")
                age_tags = []
                nums = [int(n) for n in re.findall(r"\d+", ages_raw)]

                if nums:
                    min_age, max_age = min(nums), max(nums)
                    if max_age <= 2:
                        age_tags.append("Audience - Toddler/Infant")
                    if max_age <= 4:
                        age_tags.append("Audience - Parent & Me")
                    if any(a in (3, 4) for a in nums):
                        age_tags.append("Audience - Preschool Age")
                    if max_age >= 5 and min_age <= 12:
                        age_tags.append("Audience - School Age")
                    if min_age >= 13:
                        age_tags.append("Audience - Teens")

                # Age-based category tags
                audience_keys = [a.strip() for a in ages_raw.split(",") if a.strip()]
                all_tags = []
                
                if age_to_categories:
                    for tag in audience_keys:
                        tags = age_to_categories.get(tag)
                        if tags:
                            all_tags.extend([t.strip() for t in tags.split(",")])
                
                # Add fuzzy age tags
                if age_tags:
                    all_tags.extend(age_tags)
                
                # Combine with existing program_type-based categories
                base = [c.strip() for c in categories.split(",") if c.strip()]
                combined = base + all_tags
                categories = ", ".join(dict.fromkeys(combined))

                categories = categories.replace("\u00A0", " ").replace("Â", "").strip()

                # === Normalize title and description text
                title_text = event.get("Event Name", "").lower()
                full_text = f"{event.get('Event Name', '')} {event.get('Event Description', '')}".lower()
                
                title_based_tags = []
                
                # === Match single keywords (case-insensitive)
                for keyword, cat in TITLE_KEYWORD_TO_CATEGORY.items():
                    if keyword.lower() in title_text:
                        title_based_tags.extend([c.strip() for c in cat.split(",")])
                
                # === Match combined keyword pairs (case-insensitive)
                for (kw1, kw2), cat in COMBINED_KEYWORD_TO_CATEGORY.items():
                    if kw1.lower() in full_text and kw2.lower() in full_text:
                        title_based_tags.extend([c.strip() for c in cat.split(",")])
                
                # Final deduplication
                tag_list = [c.strip() for c in categories.split(",") if c.strip()]

                # Add age-based categories
                tag_list.extend(all_tags)
                
                # Add title-based categories
                tag_list.extend(title_based_tags)
                
                # Add fallback if nothing matched
                if not tag_list:
                    # Extract just the city name from known location formats
                    raw_location = event.get("Location", "").strip()
                    fallback_city = ""
                
                    if "Norfolk" in raw_location:
                        fallback_city = "Norfolk"
                    elif "Virginia Beach" in raw_location:
                        fallback_city = "Virginia Beach"
                    elif "Chesapeake" in raw_location:
                        fallback_city = "Chesapeake"
                    elif "Portsmouth" in raw_location:
                        fallback_city = "Portsmouth"
                    elif "Hampton" in raw_location:
                        fallback_city = "Hampton"
                    elif "Newport News" in raw_location:
                        fallback_city = "Newport News"
                    elif "Suffolk" in raw_location:
                        fallback_city = "Suffolk"
                
                    fallback = f"Event Location - {fallback_city}, Audience - Free Event" if fallback_city else "Audience - Free Event"
                    tag_list.append(fallback)

                
                # Final deduplication
                categories = ", ".join(dict.fromkeys(tag_list))

                name_original = event.get("Event Name", "")
                # Remove any "@ LibraryName" from event titles before suffixing
                name_without_at = re.sub(r"\s*@\s*[^@,;:\\/]+", "", name_original, flags=re.IGNORECASE).strip()
                name_cleaned = re.sub(r"\s+at\s+.*", "", name_without_at, flags=re.IGNORECASE).strip()

                loc = event.get("Location", "")
                suffix = config.get("event_name_suffix", "")
                loc_clean = re.sub(r"^Library Branch:", "", loc).strip()
                display_loc = name_suffix_map.get(loc_clean, loc_clean)
                
                if name_cleaned.lower().endswith(display_loc.lower()):
                    event_name = f"{name_cleaned}{suffix}"
                else:
                    event_name = f"{name_cleaned} at {display_loc}{suffix}"

                if not categories:
                    categories = event.get("Categories", "") or f"Event Location - {config['organizer_name']}, Audience - Free Event, Audience - Family Event"

                row_core = [
                    event_name,
                    link,
                    event.get("Event Status", ""),
                    event.get("Time", ""),
                    event.get("Ages", ""),
                    event.get("Location", ""),
                    event.get("Month", ""),
                    event.get("Day", ""),
                    event.get("Year", ""),
                    event.get("Event Description", ""),
                    event.get("Series", ""),
                    program_type,
                    categories
                ]
                print("🧾 Raw row_core before normalize:", row_core)
                new_core = normalize(row_core)
                existing_row = existing_data.get(link, [""] * 16)
                existing_core = normalize(existing_row)

                # Flag if required fields are missing
                missing_fields = []
                if not event.get("Event Description", "").strip():
                    missing_fields.append("description")
                if not event.get("Location", "").strip():
                    missing_fields.append("location")
                
                if missing_fields:
                    site_sync_status = "REVIEW NEEDED - MISSING INFO"
                    status = "review needed"
                else:
                    status = "new"
                    site_sync_status = existing_row[15] if link in existing_data else "new"

                if link in existing_data:
                    existing_vals = {
                        "status": existing_row[2],
                        "month": existing_row[6],
                        "day": existing_row[7],
                        "year": existing_row[8],
                        "time": existing_row[3],
                    }
                    current_vals = {
                        "status": event.get("Event Status", ""),
                        "month": event.get("Month", ""),
                        "day": event.get("Day", ""),
                        "year": event.get("Year", ""),
                        "time": event.get("Time", "")
                    }
                    changed_to_cancelled = (
                        existing_vals["status"].lower() != current_vals["status"].lower()
                        and current_vals["status"].lower() == "cancelled"
                    )
                    date_changed = (
                        existing_vals["month"] != current_vals["month"]
                        or existing_vals["day"] != current_vals["day"]
                        or existing_vals["year"] != current_vals["year"]
                    )
                    time_changed = existing_vals["time"] != current_vals["time"]
                    if changed_to_cancelled or date_changed or time_changed:
                        status = "updates needed"
                        if site_sync_status == "on site":
                            site_sync_status = "updates needed"
                    else:
                        status = existing_row[14]
                        site_sync_status = site_sync_status or ""

                full_row = new_core + [now, status, site_sync_status]

                if link not in existing_data:
                    print("🔍 New row to append:", full_row)
                    new_rows.append(full_row)
                    added += 1
    
                elif new_core != existing_core:
                    print(f"🔄 Updated row {link_to_row_index[link]}:", full_row)
                    row_index = link_to_row_index[link]
                    update_requests.append({
                        "range": f"A{row_index}:Q{row_index}",
                        "values": [full_row]
                    })
                    updated += 1
            except Exception as row_err:
                print(f"❌ Error processing event: {event.get('Event Name')} — {event.get('Event Link')}")
                traceback.print_exc()
                skipped += 1

        if update_requests:
            sheet.batch_update(update_requests)

        # Export REVIEW NEEDED rows to CSV
        review_rows = [r for r in new_rows if "REVIEW NEEDED" in r[-1]]
        if review_rows:
            review_df = pd.DataFrame(review_rows, columns=headers[:len(review_rows[0])])
            review_path = f"Review Needed - Missing Info - {library}.csv"
            review_df.to_csv(review_path, index=False)
            print(f"📎 Exported {len(review_rows)} flagged rows to {review_path}")

            send_notification_email_with_attachment(
            review_path,
            f"{library.upper()} — Review Needed: Missing Info",
            config["email_recipient"]
           )


        if new_rows:
            print("🔍 Full row to upload:", full_row)
            sheet.append_rows(new_rows, value_input_option="USER_ENTERED")

        try:
            log_sheet = connect_to_sheet(SPREADSHEET_NAME, LOG_WORKSHEET_NAME)
            log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_row = [log_time, mode, added, updated, skipped]
            log_sheet.append_row(log_row, value_input_option="USER_ENTERED")
            print(f"📝 Logged summary to '{LOG_WORKSHEET_NAME}' tab.")
        except Exception as e:
            print(f"⚠️ Failed to log to {LOG_WORKSHEET_NAME} tab: {e}")

        print(f"📦 {added} new events added.")
        print(f"🔁 {updated} existing events updated.")
        if skipped:
            print(f"🧹 {skipped} malformed events skipped.")

    except Exception as e:
        print(f"❌ ERROR during upload_events_to_sheet: {e}")
        traceback.print_exc()
