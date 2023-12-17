from calendar_helper import authenticate_and_get_service, save_today_events_to_csv
import browser_handler

import schedule
import time
from datetime import datetime
import argparse
import csv
from pprint import pprint

def get_meeting():
    """API を叩いてイベント情報を取ってくる
    """
    # Google カレンダーのイベントを取得する
    service = authenticate_and_get_service()
    save_today_events_to_csv(service)
    print('Today\'s events have been saved to events.csv.')
    # 一度すべての job を消す
    schedule.clear()
    # csv のイベントを job として登録
    with open('./events.csv') as f:
        reader = csv.DictReader(f)
        for info in reader:
            info['dt_start_time'] = datetime.fromisoformat(info['Start Time'])
            add_job(info)
    pprint(schedule.get_jobs())

def launch_app(info):
    """イベント日時が迫ったらミーティングアプリを立ち上げる
    """
    # open する
    browser_handler.browser_handler(info['URL'], info['URL Type'])
    # job は定期実行として登録されているので残りをキャンセル
    schedule.clear()

def add_job(info):
    """イベント日時で job の登録
    """
    start_time = info['dt_start_time'].strftime('%H:%M')
    schedule.every().day.at(start_time).do(launch_app, info)

def main():
    browser_handler.save_credentials('Zoom')
    parser = argparse.ArgumentParser(
            prog='自動化アプリ (仮)',
            description='面倒な作業を自動化するアプリです')
    parser.add_argument('during', metavar='N', type=int, nargs=1, help='実行間隔')
    args = parser.parse_args()
    DURING = 5
    if 1 <= args.during[0]:
        DURING = args.during[0]

    # 初回
    get_meeting()
    # N分間隔で実行
    schedule.every(DURING).minutes.do(get_meeting)

    # 無限ループ
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
