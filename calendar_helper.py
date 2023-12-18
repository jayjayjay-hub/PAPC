# calendar_helper.py
from datetime import datetime, timedelta, timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import csv
import re
import os
import pickle
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request

# Google Calendar APIのスコープ
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TOKEN_PICKLE_FILE = "token.pickle"
CLIENT_SECRETS_FILE = "papc.json"

def authenticate_and_get_service():
    creds = None

    # 以前に保存されたトークンの読み込み
    if os.path.exists(TOKEN_PICKLE_FILE) and os.path.getsize(TOKEN_PICKLE_FILE) > 0:
        with open(TOKEN_PICKLE_FILE, "rb") as token:
            creds = pickle.load(token)

    # トークンが無効または存在しない場合は認証を実行
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # 認証情報を保存
        with open(TOKEN_PICKLE_FILE, "wb") as token:
            pickle.dump(creds, token)

    # サービスを構築して返す
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
    now = datetime.utcnow()
    end_time = now + timedelta(days=1)
    # 今日のすべての予定を取得
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat() + "Z",
            timeMax=end_time.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    return events
