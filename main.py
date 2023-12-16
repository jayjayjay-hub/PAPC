from datetime import datetime, timedelta, timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re
import csv

# Google Calendar APIのスコープ
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def authenticate_and_get_service():
    # Google Calendar APIの認証とサービスの取得
    flow = InstalledAppFlow.from_client_secrets_file("papc.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("calendar", "v3", credentials=creds)

def classify_url_type(url):
    # URLがZoomのものか判定
    if re.search(r"zoom\.us", url):
        return "zoom"
    # URLがGoogle Meetのものか判定
    elif re.search(r"meet\.google\.com", url):
        return "meet"
    else:
        return "else"

def get_today_and_tomorrow_events(service):
    # 現在の日本時間
    now_jp = datetime.now(timezone(timedelta(hours=9)))

    # 今日と明日の開始と終了の日時を設定
    start_of_today = datetime(now_jp.year, now_jp.month, now_jp.day, 0, 0, 0, tzinfo=timezone(timedelta(hours=9)))
    end_of_today = start_of_today + timedelta(days=1)
    start_of_tomorrow = start_of_today + timedelta(days=1)
    end_of_tomorrow = start_of_tomorrow + timedelta(days=1)

    # 今日と明日のイベントを取得
    events_result_today = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_today.isoformat(),
            timeMax=end_of_tomorrow.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events_today_and_tomorrow = events_result_today.get("items", [])

    return events_today_and_tomorrow

def write_events_to_csv(events, csv_filename):
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
                # URLの種類を判定
                URL_type = classify_url_type(URL)
                output = [start_time, URL, summary, URL_type]
                writer.writerow(output)

def main():
    # Google Calendar APIの認証とサービスの取得
    service = authenticate_and_get_service()
    print(service)

    # 今日と明日の予定を取得
    events_today_and_tomorrow = get_today_and_tomorrow_events(service)

    # 今日と明日の予定を一つのCSVに書き込む
    write_events_to_csv(events_today_and_tomorrow, 'data_today_and_tomorrow.csv')

if __name__ == "__main__":
    main()
