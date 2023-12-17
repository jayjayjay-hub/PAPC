import csv
import pprint
from pathlib import Path

from datetime import datetime, timedelta

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

flow = InstalledAppFlow.from_client_secrets_file("papc.json", SCOPES)
creds = flow.run_local_server(port=0)

service = build("calendar", "v3", credentials=creds)

# 今週の開始と終了の日時を設定
now = datetime.utcnow()
start_of_week = now - timedelta(days=now.weekday())
end_of_week = start_of_week + timedelta(days=6)

# イベントリストを取得
events_result = (
    service.events()
    .list(
        calendarId="primary",
        timeMin=start_of_week.isoformat() + "Z",
        timeMax=end_of_week.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime",
    )
    .execute()
)
events = events_result.get("items", [])


with open(__file__.replace('papc.py', '') + 'data.csv', 'w') as f:

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        if "hangoutLink" in event:
            URL = event["hangoutLink"]
            output = [start, URL, event["summary"]]
            writer = csv.writer(f)
            writer.writerow(output)

#for event in events:
#    start = event["start"].get("dateTime", event["start"].get("date"))
#    print(start, event["summary"])
#
#    event["summary"] = f'⭐️ {event["summary"]}'
#
#    updated_event = (
#        service.events()
#        .update(calendarId="primary", eventId=event["id"], body=event)
#        .execute()
#    )
