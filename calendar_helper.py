from datetime import datetime, timedelta, timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re
import webbrowser
import time

# Google Calendar APIのスコープ
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# 開いた会議のURLを保存するセット
opened_meetings = set()

def authenticate_and_get_service():
	# Google Calendar APIの認証とサービスの取得
	flow = InstalledAppFlow.from_client_secrets_file("papc.json", SCOPES)
	creds = flow.run_local_server(port=0)
	return build("calendar", "v3", credentials=creds)

def find_next_meeting_url(service):
	while True:
	# 現在の日本時間
		now_jp = datetime.now(timezone(timedelta(hours=9)))
		print(f"Checking for meetings at {now_jp}")

		# 5分おきに探す
		time_to_wait = 5 * 60
		time.sleep(time_to_wait)

		# 今日のすべての予定を取得
		events = get_today_events(service)

		for event in events:
			# 開始時刻が現在時刻より遅く、かつ、現在時刻との差が8分以内の場合
			if event["start"]["dateTime"] > now_jp and (now_jp - event["start"]["dateTime"]).total_seconds() < 480:
				meeting_url = get_meeting_url(event)
				if meeting_url and meeting_url not in opened_meetings:
					opened_meetings.add(meeting_url)
					open_meeting_url_in_browser(meeting_url)
					return meeting_url

def get_today_events(service):
	# 今日の開始と終了の日時を設定
	start_time = datetime.today()
	end_time = start_time + timedelta(days=1)

	# 今日のすべての予定を取得
	events_result = (
		service.events()
		.list(
			calendarId="primary",
			timeMin=start_time.isoformat(),
			timeMax=end_time.isoformat(),
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
