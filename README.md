## 検証環境
* Ubuntu 22.04.3
* python3.9

## 環境整備
* pythonライブラリのインストール

  ```bash
  pip install -r requirements.txt
  pip install -e .
  ```

* pre-commitのインストール

  `pre-commit install`


* .envファイルの整備

  .envファイルに以下の記述を追加
  ```
  OPENAI_API_KEY=<openaiのAPIキー>
  GITHUB_TOKEN=<github token>
  XECRETARY_SV_HOST=<チャットボットサーバーのIP>
  XECRETARY_SV_PORT=<チャットボットサーバーのPORT>
  SEND_MESSAGE_URL=<チャットレイヤーサーバのエンドポイントURL>
  CONTEXT_OBSERVER_SV_HOST=<host名>
  CONTEXT_OBSERVER_SV_PORT=<port番号>
  ```

* 外部パッケージのインストール

  `sudo apt install jq`


## ユーザーコンテキストの作成
1. 任意のディレクトリにドキュメントを置く
2. インデックスファイルを作成
    ```bash
    python src/examples/validate_index.py \
      --index-id user_context_index \
      --context-dir user_context/context
    ```
    - インデックスファイルの本体は`storage/<index ID>`に配置

## 問題集の作成
1. 任意のディレクトリにyamlファイルを作成
2. yamlファイルに下記を記述
    ```yaml
    - evaluation: null # 評価値
      human_answer: null # 人間による評価文
      input: <AIへの質問> # AIへの質問
      output: null # AIの回答
    ```

## 設定ファイルの作成
- [リンク参照](./how_to_config.md)

## エージェント実行
```bash
python src/examples/validate_main.py --conf-toml conf/test.toml
```

## β版サーバー
### 起動
```bash
. script/run_beta_sv.sh
```

### 停止
```bash
. script/stop_beta_sv.sh
```
