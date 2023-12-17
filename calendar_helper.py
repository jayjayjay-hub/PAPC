from datetime import datetime, timedelta, timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re
import webbrowser
import time
import csv

# Google Calendar APIのスコープ
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def authenticate_and_get_service():
	# Google Calendar APIの認証とサービスの取得
	flow = InstalledAppFlow.from_client_secrets_file("papc.json", SCOPES)
	creds = flow.run_local_server(port=0)
	return build("calendar", "v3", credentials=creds)

def find_next_meeting_url(service):
	# 今日のすべての予定を取得
	events = get_today_events(service)
	write_csv(events, "events.csv")

def write_csv(events, csv_filename):
    # CSVファイルに予定を書き込む
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Start Time", "URL", "Summary"])
        # 予定をCSVに書き込む
        for event in events:
            summary = event.get("summary", "No Title")
            start_time = event["start"].get("dateTime", event["start"].get("date"))
            # Google Meetの場合はhangoutLinkを使用し、それ以外はdescriptionからURLを抽出
            if "hangoutLink" in event:
                URL = event["hangoutLink"]
            else:
                description = event.get("description", "")
                URL_match = re.search(r"<a\s+href=\"(?P<url>https?://[^\"]+)\">", description)
                URL = URL_match.group("url") if URL_match else "No URL"

            # URLがあればCSVに書き込む
            if URL != "No URL":
                output = [start_time, URL, summary]
                # URLの種類を判定
                URL_type = classify_url_type(URL)
                output = [start_time, URL, summary, URL_type]
                writer.writerow(output)

def classify_url_type(url):
    # URLがZoomのものか判定
    if re.search(r"zoom\.us", url):
        return "zoom"
    # URLがGoogle Meetのものか判定
    elif re.search(r"meet\.google\.com", url):
        return "meet"
    else:
        return "else"

def get_today_events(service):
    # 今日の開始と終了の日時を設定
    now = datetime.utcnow().isoformat() + "Z"
    print(now)
    end_time = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
	# 今日のすべての予定を取得
    events_result = (
		service.events()
		.list(
			calendarId="primary",
			timeMin=now,
			timeMax=end_time,
			singleEvents=True,
			orderBy="startTime",
		)
		.execute()
	)
    events = events_result.get("items", [])
    return events

def get_meeting_url(event):
	summary = event.get("summary", "No Title")
	start_time = event["start"].get("dateTime", event["start"].get("date"))

	# Google Meetの場合はhangoutLinkを使用し、それ以外はdescriptionからURLを抽出
	if "hangoutLink" in event:
		return event["hangoutLink"]
	else:
		description = event.get("description", "")
		URL_match = re.search(r"<a\s+href=\"(?<url>https?://[^\"]+)\">", description)
		return URL_match.group("url") if URL_match else None

def open_meeting_url_in_browser(meeting_url):
	# ブラウザでURLを開く
	webbrowser.open(meeting_url)
