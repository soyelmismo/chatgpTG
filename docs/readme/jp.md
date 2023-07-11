- ボット：https://t.me/chismegptbpt

[![jp](https://img.shields.io/badge/変数-jp-blueviolet)](https://gg.resisto.rodeo/yo/chatgpTG/src/branch/main/docs/variables/jp.md)

## コマンド：
- /new - 新しい対話を開始します。
- /img - 画像を生成します。
- /retry - ボットの最後の応答を再生成します。
- /chat_mode - チャットモードを選択します。
- /model - AIモデルを表示します。
- /api - APIを表示します。
- /lang - 利用可能な言語を表示します。
- /status - 現在の設定を表示します：モデル、チャットモード、API。
- /reset - 設定をデフォルト値にリセットします。
- /search - インターネットで検索します。
- /help - このメッセージを再表示します。

## 特徴：
- 関数の呼び出し！（直接GPTに接続されたプラグイン、6月のモデル>）。
- ローカルのJSONデータベース。
- 非常にモジュラーでカスタマイズ可能。
- /searchを使用してGPTがインターネットにアクセスできるようにします！
- テキストファイル、PDF、またはURLを送信して、ボットがそれらを分析できます！
- 必要に応じてOpenAIの逆プロキシとそれに対応するモデルを追加できます！
- マルチ言語対応。
- 画像のテキストを読み取ります。
- 音声を転写します。

# 重要：
- カスタムAPIは、OpenAIと同じ構造に従う必要があります。つまり、「https://dominio.dom/v1/...」です。

## セットアップ
1. [OpenAI API](https://openai.com/api/)からAPIキーを取得します。

2. Telegramのボットトークンを[@BotFather](https://t.me/BotFather)から取得します。

3. `config/api.example.json`を編集してAPIキーを設定するか、カスタムAPIを追加します。

4. Telegramのトークン、Mongoデータベース、その他の変数を`docker-compose.example.yml`で変更し、`docker-compose.example.yml`を`docker-compose.yml`に名前を変更します。

5. 🔥 ターミナルからディレクトリにアクセスし、**実行**します：
    ```bash
    docker-compose up --build
    ```
# スターの履歴

<a href="https://gg.resisto.rodeo/yo/chatgpTG"><img width="500" alt="Star History Chart" src="https://api.star-history.com/svg?repos=soyelmismo/chatgpTG&type=Date"></a> 

## 参考文献
1. 元のソースコード：<a href="https://github.com/karfly/chatgpt_telegram_bot" alt="Karfly">Karfly/chatgpt_telegram_bot</a>