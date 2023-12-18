import schedule
import time
from datetime import datetime, timedelta, timezone
import zoneinfo
import argparse
import csv
from pprint import pprint

from calendar_helper import authenticate_and_get_service, save_today_events_to_csv
import browser_handler

def get_meeting(service):
    print("Getting today's events...")
    """API を叩いてイベント情報を取ってくる
    """
    # Google カレンダーのイベントを取得する
    save_today_events_to_csv(service)
    print('Today\'s events have been saved to events.csv.')
    try:
        # 一度すべての job を消す
        schedule.clear()
        # csv のイベントを job として登録
        with open('./events.csv') as f:
            reader = csv.DictReader(f)
            for info in reader:
                info['dt_start_time'] = datetime.fromisoformat(info['Start Time'])
                add_job(info)
        print("saccsess to add job")
        pprint(schedule.get_jobs())
    except Exception as e:
        print("*****************************************************\n\n\n")
        print(f"Error: {e}")
        print("\n\n\n*****************************************************")

def launch_app(info):
    """イベント日時が迫ったらミーティングアプリを立ち上げる
    """
    # open する
    if len(info['URL']) == 0:
        return
    browser_handler.browser_handler(info['URL'], info['URL Type'])
    # job は定期実行として登録されているので残りをキャンセル
    schedule.clear()

def add_job(info):
    """イベント日時で job の登録
    """
    print("add_job")
    now = datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo'))
    # now = datetime.now(timezone(timedelta(hours=12)))
    print(f"now : {now}")
    start = info['dt_start_time']
    print(f"start : {start}")
    start_b5m = start - timedelta(minutes=5)
    if start_b5m > now:
        job_time = start_b5m.strftime('%H:%M')
        print(f"job_time 5min: {job_time}")
    elif start > now:
        job_time = start.strftime('%H:%M')
        print(f"job_time : {job_time}")
    else:
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&\n\n\n")
        print("else")
        print("\n\n\n&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        return
    schedule.every().day.at(job_time).do(launch_app, info)

def main():
    browser_handler.save_credentials('Zoom')
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

    print('Start main loop.')

    # 無限ループ
    while True:
        # event を取得
        get_meeting(service)
        # N秒待機
        print(f'Waiting for {DURING} minutes...')
        time.sleep(DURING * 60)
        # スケジュール実行
        schedule.run_pending()

if __name__ == '__main__':
    main()
