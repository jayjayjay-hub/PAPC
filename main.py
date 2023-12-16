from flask import Flask, render_template
from calendar_helper import authenticate_and_get_service, find_next_meeting_url

app = Flask(__name__)

# Google Calendar APIの認証とサービスの取得
service = authenticate_and_get_service()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/next_meeting')
def next_meeting():
    # ここに直近5分以内の会議URLを取得するロジックを追加
    meeting_url = find_next_meeting_url(service)
    return render_template('next_meeting.html', meeting_url=meeting_url)

if __name__ == "__main__":
    app.run(debug=False)
