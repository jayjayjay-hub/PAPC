# <h1 align="center">
#     自動ミーティングオープナー
# </h1>

## 💡 プロジェクトについて

> _このプロジェクトは、〔【株式会社ケアリッツ・テクノロジーズ × 42 Tokyo】2Daysワークショップ『Python自動化プログラムコンテスト』〕で作成されたものです_

    毎日のミーティングの管理を簡略化し、ミーティングアプリの起動を自動化することを目指しています。
    このアプリケーションを使用すれば、ミーティングの開始時刻を忘れてしまっていても問題ありません。
    GoogleカレンダーAPIを使用してイベントを取得し、指定された間隔でミーティングをスケジュールします。

## 主な機能一覧:

### [main.py](main.py)

* `get_meeting(service)`: GoogleカレンダーAPIから今日のイベントを取得し、それをCSVファイルに保存します。
* `launch_app(info)`: イベントの開始時間が近づくと、ミーティングアプリを起動します。
* `add_job(info)`: イベントの開始時間に基づいてジョブをスケジュールに追加します。
* `main()`: アプリケーションのメインループで、Googleカレンダーと認証し、スケジューリングプロセスを実行します。

### [calendar_helper.py](calendar_helper.py)

* `authenticate_and_get_service()`: GoogleカレンダーAPIと認証し、サービスオブジェクトを返します。
* `save_today_events_to_csv(service)`: 今日のイベントを取得し、それらをCSVファイルに保存します。
* イベントデータの処理、タイムゾーンの変換、会議URLの分類など、さまざまなユーティリティ関数が含まれています。

### [browser_handler.py](browser_handler.py)

* `save_credentials(*services)`: Zoomの認証情報をJSONファイルに安全に保存します。
* `run_applescript(url)`: ミーティングをGoogle Chromeで開くためのScriptを実行します。
* `browser_handler(url, meeting_type='meet')`: 指定されたミーティングURLを適切なブラウザで開きます。

### [app.py](app.py), [static/](static), [templates/](templates)

unfinished

## 🚀 使用方法

### 必要なもの

プロジェクトにはPython 3.7以上といくつかの外部ライブラリが必要です。これらは次のコマンドでインストールできます。

```shell
$ pip install -r requirements.txt
```

### 手順

**・APIの取得は自分で行うこと**

**・macOSはmasterブランチ、WSL2はWindowsブランチのコードを使用すること**

アプリケーションを実行します

```shell
$ python main.py x
```

1. x : カレンダーからイベントを取得する間隔を分単位で入力してください。何も入力しないと5分に設定されます。
2. Zoomアカウント情報登録：ZoomアカウントのIDとパスワードを登録してください
```shell
$ Enter your Zoom ID: {your ID}
$ Enter your Zoom password: {your password}
```
  二回目以降は次のように聞かれるのでIDとpasswordに変更がなければ**no**を入力してください
```shell
'credentials.json' already exists. Do you want to update it? (yes/no):
```
3. Googleカレンダー認証：画面に従ってください。
