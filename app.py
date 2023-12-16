from flask import Flask, render_template, redirect, url_for
from calendar_helper import authenticate_and_get_service, find_next_meeting_url
from selenium import webdriver
import threading
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


app = Flask(__name__)

# Google Calendar APIの認証とサービスの取得
service = authenticate_and_get_service()

# ChromeDriverManagerの読み込み
webdriver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=webdriver_service)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/next_meeting')
def next_meeting():
    # ここに直近5分以内の会議URLを取得するロジックを追加
    meeting_url = find_next_meeting_url(service)
    return render_template('next_meeting.html', meeting_url=meeting_url)

def run_selenium():
    # Seleniumを使用してブラウザを操作
    driver.get("http://127.0.0.1:5000/")

    # "起動"ボタンをクリック
    start_button = driver.find_element_by_id('startButton')
    start_button.click()

    # ウェイトしてからブラウザを閉じる
    time.sleep(2)
    driver.quit()

# Flaskアプリケーションを別スレッドで起動
flask_thread = threading.Thread(target=app.run, kwargs={'debug': False})
flask_thread.start()

# Seleniumを別スレッドで実行
selenium_thread = threading.Thread(target=run_selenium)
selenium_thread.start()

# メインスレッドがSeleniumとFlaskのスレッドの終了を待つ
selenium_thread.join()
flask_thread.join()

if __name__ == "__main__":
    app.run(debug=False)
