from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re
import webbrowser

# Google Calendar APIのスコープ
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def authenticate_and_get_service():
    flow = InstalledAppFlow.from_client_secrets_file("papc.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("calendar", "v3", credentials=creds)

def main():
    # Google Calendar APIの認証とサービスの取得
    service = authenticate_and_get_service()
    print(service)

    # 今日の開始と終了の日時を設定
    now = datetime.utcnow()
    start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
    end_of_day = start_of_day + timedelta(days=1)

    # 今日のイベントを取得
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day.isoformat() + "Z",
            timeMax=end_of_day.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    # 今日の予定を確認し、URLがあれば開く
    for event in events:
        summary = event.get("summary", "No Title")
        start_time = event["start"].get("dateTime", event["start"].get("date"))
        print(f"Event: {summary}, Start Time: {start_time}")

        # 予定の詳細を確認
        description = event.get("description", "")
        print(f"Description: {description}")

		# 詳細中にURLがあれば開く
        url_match = re.search(r"<a\s+href=\"(?P<url>https?://[^\"]+)\">", description)
        if url_match:
              url_to_output = url_match.group("url")
              print(f"Opening URL: {url_to_output}")


if __name__ == "__main__":
    main()
