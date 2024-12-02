# AI Auto Gameplay System

AIを活用してNintendo Switchのゲームを自動プレイするためのフレームワークです。OBSで取得したゲーム画面をAIが解析し、適切な操作判断を行い、Arduino互換機を介してNintendo Switchを自動操作します。
https://www.youtube.com/watch?v=dRsVVPaOOVk

### 主な機能

- OBS Studioを使用したNintendo Switch画面のキャプチャ
- OpenAI GPTを使用した画面認識と状況判断
- Arduino互換機を使用したNintendo Switchコントローラーのエミュレーション
- MongoDBを使用したプレイログの保存
- Webhookによる外部システムとの連携

## システム要件

- Python 3.8以上
- OBS Studio
- Arduino互換機（Nintendo Switchコントローラーエミュレーション用）
- MongoDB Atlas アカウント
- OpenAI API アカウント

## インストール

1. リポジトリのクローン
```bash
git clone https://github.com/ai-asa/ai-auto-gameplay-system-v2.git
cd ai-auto-gameplay-system
```

2. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

3. 設定ファイルの準備
   - `settings/settings.ini`に以下の設定を行う
     - OpenAI APIキー
     - OBS WebSocket設定
     - MongoDB接続情報
     - シリアルポート設定
     - Webhook URL

## 設定ファイル

### settings.ini
```ini
[ENVIRONMENT]
openai_api_key = your-api-key

[OBS]
obs_ws_host = 127.0.0.1
obs_ws_port = 4455
obs_ws_password = your-password

[SYSTEM]
serial_port_com = COM3
serial_baud_rate = 115200
source_path = Switch画面

[MONGODB]
user_name = your-username
password = your-password
app_name = your-app-name
```

### gameplay_config.ini
```ini
[GAMEPLAY]
game_title = ゲームタイトル
save_name = セーブデータ名
play_target = プレイ目標
game_info = ゲーム情報ファイル名
```

## 使用方法

システムの起動方法は以下の2種類があります：

### 1. コマンドライン引数による起動
```bash
python main.py --game-title "ゲームタイトル" --save-name "セーブデータ名" --play-target "プレイ目標" --game-info "ゲーム情報ファイル名"
```

### 2. 設定ファイルによる起動
1. `config/gameplay_config.ini`に必要な情報を設定
2. 以下のコマンドで起動
```bash
python main.py
```

## システム構成

### コアモジュール
- `main.py`: システムのエントリーポイント
- `game_play_system.py`: ゲームプレイのメインロジック

### アダプターモジュール
- `obs_websocket_adapter.py`: OBS Studioとの連携
- `switch_controller_adapter.py`: Nintendo Switchコントローラーの制御
- `openai_adapter.py`: OpenAI APIとの通信
- `mongo_adapter.py`: MongoDBとのデータ連携
- `webhook_adapter.py`: 外部システムとの連携

### その他のモジュール
- `logger_config.py`: ログ設定
- `get_prompt.py`: AIプロンプトの生成

## ログ機能

- プレイログはMongoDBに保存
- 各ログには以下の情報が含まれます：
  - タイムスタンプ
  - AIの判断内容
  - 実行された操作
  - 選択されたボタンコマンド

## 注意事項

1. Arduino互換機は適切なファームウェアを書き込み、Nintendo Switchコントローラーとして認識される状態にしてください。
2. シリアルポートの設定は、Arduino互換機が接続されているポートに合わせて設定してください。
3. OBS StudioのWebSocket設定は、セキュリティを考慮して適切なパスワードを設定してください。
4. MongoDBの接続情報は、適切なアクセス制限を設定してください。
5. OpenAI APIキーは外部に漏れないよう、適切に管理してください。

## トラブルシューティング

1. コントローラー接続エラー
   - Arduino互換機の接続を確認
   - COMポートの設定を確認
   - ファームウェアが正しく書き込まれているか確認

2. OBS接続エラー
   - OBS Studioが起動していることを確認
   - WebSocket設定を確認
   - キャプチャーソースの名前が設定と一致しているか確認

3. MongoDB接続エラー
   - インターネット接続を確認
   - 認証情報を確認
