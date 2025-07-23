import gspread
import pandas as pd
from datetime import datetime
import base64
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import smtplib
from email.mime.text import MIMEText
import re
from config import get_library_config
from constants import LIBRARY_CONSTANTS
from gspread.utils import rowcol_to_a1
import unicodedata
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart

def send_notification_email_with_attachment(file_path, subject, recipient):
    smtp_user = os.environ["SMTP_USERNAME"]
    smtp_pass = os.environ["SMTP_PASSWORD"]

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg.attach(MIMEText("Your new CSV export is attached."))

    # Attach file
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    print(f"📧 Email with attachment sent to {recipient}")


def _ascii_normalize(val):
    if not isinstance(val, str):
        return val
    # Normalize to NFKD and encode to ASCII, ignoring errors
    return unicodedata.normalize("NFKD", val).encode("ascii", "ignore").decode("ascii")


def infer_location_from_title(title, name_suffix_map):
    match = re.search(r"@ ([\w\- ]+)", title)
    if not match:
        return ""
    short_name = match.group(1).strip()
    for full, short in name_suffix_map.items():
        if short_name.lower() in short.lower():
            return full
    return ""

# === UTILITY FUNCTIONS ===
def _format_time(raw: str) -> str:
    if not raw:
        return ""
    txt = raw.lower().replace("–", "-").replace("—", "-").replace(".", "")
    txt = re.sub(r"(\d)([ap]m)", r"\1 \2", txt).strip()
    for fmt in ("%I:%M %p", "%I %p"):
        try:
            return datetime.strptime(txt, fmt).strftime("%-I:%M %p") if ":" in txt else datetime.strptime(txt, fmt).strftime("%-I %p")
        except ValueError:
            continue
    return txt.upper()

def _split_times(time_str: str):
    if not time_str or time_str.strip().lower() in ("all day", "all day event", "ongoing"):
        return "", "", "TRUE"
    parts = re.split(r"\s*[-–—]\s*", time_str)
    start = _format_time(parts[0] if parts else "")
    end = _format_time(parts[1] if len(parts) > 1 else "")
    return start, end, "FALSE"

def _ascii_quotes(val):
    if not isinstance(val, str):
        return val
    return val.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')

def upload_csv_to_drive(csv_path, creds, folder_id):
    drive_service = build("drive", "v3", credentials=creds)
    file_metadata = {"name": os.path.basename(csv_path), "parents": [folder_id]}
    media = MediaFileUpload(csv_path, mimetype="text/csv")
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = uploaded_file.get("id")
    return f"https://drive.google.com/file/d/{file_id}/view"

def send_notification_email(file_url, subject, recipient):
    smtp_user = os.environ["SMTP_USERNAME"]
    smtp_pass = os.environ["SMTP_PASSWORD"]

    msg = MIMEText(f"A new CSV export is ready:\n\n{file_url}")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    print(f"📬 Email sent to {recipient}")

def export_events_to_csv(library="vbpl"):
    config = get_library_config(library)
    constants = LIBRARY_CONSTANTS.get(library, {})
    name_suffix_map = constants.get("name_suffix_map", {})
    suffix = config.get("event_name_suffix", "")

    creds = service_account.Credentials.from_service_account_file(
        "/etc/secrets/GOOGLE_APPLICATION_CREDENTIALS_JSON",
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/gmail.send"
        ]
    )

    client = gspread.authorize(creds)
    sheet = client.open(config["spreadsheet_name"]).worksheet(config["worksheet_name"])
    df = pd.DataFrame(sheet.get_all_records())

    # 🔧 Convert all columns to string safely
    for col in df.columns:
        df[col] = df[col].astype(str)

    original_row_count = len(df)

    required_columns = [
        "Event Name", "Location", "Categories", "Program Type", "Series", "Event Description",
        "Event Link", "Month", "Day", "Year", "Event End Date", "Site Sync Status",
        "Venue", "EVENT START DATE", "EVENT START TIME", "EVENT END DATE", "EVENT END TIME", "ALL DAY EVENT"
    ]
    for col in required_columns:
        if col not in df.columns:
            print(f"🔨 Creating missing column: {col}")
            df[col] = ""
        else:
            df[col] = df[col].fillna("").astype(str)
            

    print("\n🔎 Column counts before filtering:")
    for col in [
        "Event Name", "Venue", "EVENT START DATE", "EVENT START TIME", "EVENT END DATE",
        "EVENT END TIME", "ALL DAY EVENT", "Categories", "Event Link", "Event Description"
    ]:
        print(f"{col}: {len(df[col])}" if col in df.columns else f"❌ Missing column: {col}")
    
    # ✅ These lines must be OUTSIDE the loop above
    for col in df.columns:
        df[col] = df[col].astype(str)
    
    # 🧪 DEBUG BLOCK
    print("\n🔬 Dtypes snapshot before filtering:")
    print(df.dtypes)
    
    print("\n🔍 Any non-strings in 'Event Name'?")
    print(df[~df["Event Name"].apply(lambda x: isinstance(x, str))])
    
    # ✅ Filter and exclude
    df = df[df["Site Sync Status"].fillna("").str.strip().str.lower() == "new"]
    df = df[~df["Event Name"].str.lower().str.contains("artist of the month")]
    
    if df.empty:
        print("🚫  No new events to export.")
        return

    # Exclude any event where the only age tag is adult-related
    df["Ages"] = df["Ages"].fillna("").astype(str)
    # Custom exclusion: skip if Ages is exactly one of these problematic combinations
    EXACT_EXCLUDE_AGES = {
        "adult", "adults", "adults 18+", "18+", "adults (18+), all ages"
    }
    
    df["Ages"] = df["Ages"].fillna("").astype(str).str.strip().str.lower()
    df = df[~df["Ages"].isin(EXACT_EXCLUDE_AGES)]

    df["Event Status"] = df["Event Status"].fillna("").astype(str)
    df = df[~df["Event Status"].str.strip().str.lower().eq("cancelled")]

    # ✅ Add another short-circuit here
    if df.empty:
        print("🚫  No new events to export (after age filters).")
        return
    # 🔎 Debug: Check for non-string issues in Categories
    print("Categories type preview:")
    print(df["Categories"].apply(lambda x: f"{type(x)} - {x}" if pd.notnull(x) else "None").head(10))
    
    # ✅ Enforce type before using .str.contains
    df["Program Type"] = df["Program Type"].fillna("").astype(str)
    df["Categories"] = df["Categories"].fillna("").astype(str)
    
    df = df[~df["Program Type"].str.contains("Classes & Workshops", case=False)]
    df = df[~df["Categories"].str.contains("Classes & Workshops", case=False)]

    time_info = df["Time"].astype(str).apply(_split_times)
    time_df = pd.DataFrame(time_info.tolist(), index=df.index, columns=["start", "end", "all_day"])
    df[["EVENT START TIME", "EVENT END TIME"]] = time_df[["start", "end"]]
    df["ALL DAY EVENT"] = time_df["all_day"]
    df.loc[df["ALL DAY EVENT"] == "TRUE", ["EVENT START TIME", "EVENT END TIME"]] = ["", ""]

    df["Month"] = df["Month"].astype(str)
    df["Day"] = df["Day"].astype(str)
    df["Year"] = df["Year"].astype(str)
    
    month_str = df["Month"] + " " + df["Day"] + " " + df["Year"]
    
    df["EVENT START DATE"] = pd.to_datetime(month_str, format="%b %d %Y", errors="raise").dt.strftime("%Y-%m-%d")
    df["EVENT END DATE"] = df["Event End Date"].fillna("").astype(str)
    df.loc[df["EVENT END DATE"].str.strip() == "", "EVENT END DATE"] = df["EVENT START DATE"]
    df["EVENT END DATE"] = df["EVENT END DATE"].fillna("").astype(str)

    df["Location"] = df.apply(
        lambda row: infer_location_from_title(row["Event Name"], name_suffix_map)
        if not str(row["Location"]).strip() else row["Location"], axis=1
    )

    venue_map = constants.get("venue_names") or name_suffix_map

    df["Venue"] = (
        df["Location"]
          .str.replace(r"^Library Branch:", "", regex=True)
          .str.strip()
          .map(venue_map)
          .fillna(df["Location"].str.replace(r"^Library Branch:", "", regex=True).str.strip())
    )

    def format_event_title(row):
        base = re.sub(r"\s+at\s+.*", "", row["Event Name"]).strip()
        loc_clean = re.sub(r"^Library Branch:", "", row["Location"]).strip()
        suffix_name = name_suffix_map.get(loc_clean, loc_clean)
        return f"{base} at {suffix_name}{suffix}" if suffix_name else base + suffix

    df["Event Name"] = df.apply(format_event_title, axis=1)

    expected_export_cols = [
        "Event Name", "Venue", "EVENT START DATE", "EVENT START TIME", "EVENT END DATE",
        "EVENT END TIME", "ALL DAY EVENT", "Categories", "Event Link", "Event Description"
    ]
    for col in expected_export_cols:
        if col not in df.columns:
            df[col] = ""
        else:
            df[col] = df[col].fillna("").astype(str)

    print("\n🔍 Final export column lengths:")
    for col in expected_export_cols:
        print(f"{col}: {len(df[col])}")

    export_df = pd.DataFrame({
        "EVENT NAME": df["Event Name"],
        "EVENT EXCERPT": "",
        "EVENT VENUE NAME": df["Venue"],
        "EVENT ORGANIZER NAME": config["organizer_name"],
        "EVENT START DATE": df["EVENT START DATE"],
        "EVENT START TIME": df["EVENT START TIME"],
        "EVENT END DATE": df["EVENT END DATE"],
        "EVENT END TIME": df["EVENT END TIME"],
        "ALL DAY EVENT": df["ALL DAY EVENT"],
        "TIMEZONE": "America/New_York",
        "HIDE FROM EVENT LISTINGS": "FALSE",
        "STICKY IN MONTH VIEW": "FALSE",
        "EVENT CATEGORY": df["Categories"],
        "EVENT TAGS": "",
        "EVENT COST": "",
        "EVENT CURRENCY SYMBOL": "$",
        "EVENT CURRENCY POSITION": "",
        "EVENT ISO CURRENCY CODE": "USD",
        "EVENT FEATURED IMAGE": "",
        "EVENT WEBSITE": df["Event Link"],
        "EVENT SHOW MAP LINK": "TRUE",
        "EVENT SHOW MAP": "TRUE",
        "ALLOW COMMENTS": "FALSE",
        "ALLOW TRACKBACKS AND PINGBACKS": "FALSE",
        "EVENT DESCRIPTION": df["Event Description"]
    })

    str_cols = export_df.select_dtypes(include="object").columns
    for col in str_cols:
        export_df[col] = export_df[col].map(_ascii_normalize).map(_ascii_quotes)


    csv_path = f"events_for_upload_{library}.csv"
    export_df.to_csv(csv_path, index=False)
    print(f"✅ Exported {len(export_df)} events to CSV (from {original_row_count} original rows)")

    send_notification_email_with_attachment(csv_path, config["email_subject"], config["email_recipient"])

    # ✅ Mark exported rows as "on site" in the sheet
    site_sync_col = df.columns.get_loc("Site Sync Status")
    values = sheet.get_all_values()

    # Build a map from Event Link → Sheet Row Number
    link_col_idx = df.columns.get_loc("Event Link")
    event_link_to_row = {}

    for i, row in enumerate(values[1:], start=2):  # Skip header
        if len(row) > link_col_idx:
            link = row[link_col_idx].strip()
            if link:
                event_link_to_row[link] = i

    # Prepare batch updates
    updates = []
    for link in df["Event Link"]:
        link = str(link).strip()
        row_num = event_link_to_row.get(link)

        if row_num:
            cell = rowcol_to_a1(row_num, site_sync_col + 1)
            updates.append({"range": cell, "values": [["on site"]]})

    # Perform batch update
    if updates:
        sheet.batch_update([{"range": u["range"], "values": u["values"]} for u in updates])

    return csv_path

if __name__ == "__main__":
    LIBRARIES = ["chpl"]
    print("🧪 Running export_to_csv.py with LIBRARIES:", LIBRARIES)
    for lib in LIBRARIES:
        print(f"\n📁 Exporting events for: {lib.upper()}")
        try:
            export_events_to_csv(lib)
        except Exception as e:
            print(f"❌ Failed to export for {lib}: {e}")
