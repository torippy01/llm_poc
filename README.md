## 検証環境
* Ubuntu 22.04.3
* python3.9

## 環境整備
* pythonライブラリのインストール

  `pip install -r requirements.txt`

* pre-commitのフックスクリプトをインストール

  `pre-commit install`

* .envファイルの整備

  .envファイルに以下の記述を追加
  ```
  OPENAI_API_KEY=<openaiのAPIキー>
  XECRETARY_SV_HOST=<チャットボットサーバーのIP>
  XECRETARY_SV_PORT=<チャットボットサーバーのPORT>
  SEND_MESSAGE_URL=<チャットレイヤーサーバのエンドポイントURL>
  ```

## ユーザーコンテキストの作成
1. 任意のディレクトリにドキュメントを置く
2. インデックスファイルを作成
    ```bash
    python src/validate_ci.py \
      --index-id user_context_index \
      --context-dir user_context/context
    ```
    - インデックスファイルの本体は`storage/<index ID>`に配置

## 問題集の作成
1. 任意のディレクトリにyamlファイルを作成
2. yamlファイルに下記を記述
    ```yaml
    - evaluation: null
      human_answer: null
      input: <AIへの質問>
      output: null
    ```
    - `evaluation`: 評価値
    - `human_answer`: 人間による評価文
    - `input`: AIへの質問
    - `output`: AIの回答

## 設定ファイルの作成
- [リンク参照](./how_to_config.md)

## エージェント実行
```bash
python src/validate.py --conf-toml conf/test.toml
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

## 検証レポート
* ✅ [文量がインデックス化に与える影響の検証](./repo/report_doc_num.md)
* ✅ [コンテキストなしの自然言語からAWS CLIのコマンドを実行させる検証](./repo/report_exec_command_contextless.md)
* ✅ [コンテキストつきの自然言語からAWS CLIのコマンドを実行させる検証](./repo/report_exec_command_context.md)
* ✅ [コンテキストなしの質問をコンテキストを考慮するエージェントにしてみた](./repo/report_contextless_request_with_usercontext.md)
* ✅ [対話方法を網羅的に調査](./repo/report_conversational_pickup.md)
* ✅ [対話的エージェントの検証](./repo/report_conversational.md)
