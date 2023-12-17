# calendar_helper.py
from datetime import datetime, timedelta, timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import csv
import re
from bs4 import BeautifulSoup

# Google Calendar APIのスコープ
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def authenticate_and_get_service():
    # Google Calendar APIの認証とサービスの取得
    flow = InstalledAppFlow.from_client_secrets_file("papc.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("calendar", "v3", credentials=creds)

def save_today_events_to_csv(service):
    # 今日のイベントを取得
    events = get_today_events(service)

    # イベントをCSVに保存
    write_csv(events, "events.csv")

def write_csv(events, csv_filename):
    # CSVファイルにイベントを書き込む
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Event Name", "URL", "URL Type", "Start Time"])
        for event in events:
            event_name = event.get("summary", "No Title")
            start_time = event["start"].get("dateTime", event["start"].get("date"))
            # 日本時間に変換
            start_time = convert_to_jst(start_time)
            # url, url_type = get_meeting_url_and_type(event)
            url = get_meeting_url(event)
            url_type = classify_url_type(url)
            writer.writerow([event_name, url, url_type, start_time])

def extract_url_from_description(description):
    # リッチテキストであるかどうかを判定
    is_rich_text = bool(BeautifulSoup(description, 'html.parser').find())

    if is_rich_text:
        # リッチテキストの場合
        soup = BeautifulSoup(description, 'html.parser')
        link = soup.find('a')
        if link and 'href' in link.attrs:
            return link['href']
    elif description is not None:
        # プレーンテキストの場合
        URL_match = re.search(r"https?://[^\s]+", description)
        if URL_match:
            return URL_match.group()
    return None

def get_meeting_url(event):
    if event is not None:
        # Google Meetの場合はhangoutLinkを使用し、それ以外はdescriptionからURLを抽出
        if "hangoutLink" in event:
            url = event["hangoutLink"]
        else:
            url = extract_url_from_description(event.get("description", ""))
        return url
    else:
        return None

def convert_to_jst(utc_time):
    # UTC時間を日本時間に変換する関数
    jst = timezone(timedelta(hours=9))  # 日本時間のタイムゾーン
    return datetime.fromisoformat(utc_time).astimezone(jst).isoformat()

def classify_url_type(url):
    if url is not None:
        # URLがZoomのものか判定
        if re.search(r"zoom.us", url):
            return "Zoom"
        # URLがGoogle Meetのものか判定
        elif re.search(r"meet.google.com", url):
           return "Google Meet"
        else:
            return "Other"
    else:
        return "No URL"

def get_today_events(service):
    # 今日の開始と終了の日時を設定
    now = datetime.utcnow().isoformat() + "Z"
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
