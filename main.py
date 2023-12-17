import schedule
import time
from datetime import datetime, timedelta
import zoneinfo
import argparse
import csv
from pprint import pprint

from calendar_helper import authenticate_and_get_service, save_today_events_to_csv
import browser_handler

def get_meeting(service):
    """API を叩いてイベント情報を取ってくる
    """
    # Google カレンダーのイベントを取得する
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
    if info['URL Type'] == 'Zoom':
        browser_handler.save_credentials('Zoom')
    if len(info['URL']) == 0:
        return
    browser_handler.browser_handler(info['URL'], info['URL Type'])
    # job は定期実行として登録されているので残りをキャンセル
    schedule.clear()

def add_job(info):
    """イベント日時で job の登録
    """
    info['dt_start_time']
    now = datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo'))
    start = info['dt_start_time']
    start_b5m = start - timedelta(minutes=5)
    if start_b5m > now:
        job_time = start_b5m.strftime('%H:%M')
    elif start > now:
        job_time = start.strftime('%H:%M')
    else:
        return
    schedule.every().day.at(job_time).do(launch_app, info)

def main():
    parser = argparse.ArgumentParser(
            prog='自動化アプリ (仮)',
            description='面倒な作業を自動化するアプリです')
    parser.add_argument('during', metavar='N', type=int, nargs='?', default=5, help='実行間隔')
    args = parser.parse_args()
    if 1 <= args.during:
        DURING = args.during

    # 初回
    service = authenticate_and_get_service()
    get_meeting(service)
    # N分間隔で実行
    schedule.every(DURING).minutes.do(get_meeting, service)

    # 無限ループ
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
