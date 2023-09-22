## 検証環境
* Ubuntu 22.04.3
* python3.9

## 環境整備
* pythonライブラリのインストール

  `pip install -r requirements.txt`

* .envファイルの整備

  .envファイルに以下の記述を追加
  ```
  OPENAI_API_KEY="<openaiのAPIキー>"
  ```

## 実行
```bash
streamlit run <pythonファイルのパス>
```

## 検証レポート
* ✅ [文量がインデックス化に与える影響の検証](./repo/report_doc_num.md)
* ✅ [コンテキストなしの自然言語からAWS CLIのコマンドを実行させる検証](./repo/report_exec_command_contextless.md)
* ✅ [コンテキストつきの自然言語からAWS CLIのコマンドを実行させる検証](./repo/report_exec_command_context.md)
* 🔜 ドキュメントの前処理方法の検討
* 🔜 入力トークン数が多い場合の対処法の検討
* 🔜 多量のAWS CLIインデックスの扱い方の検討
* 🔜 コマンド実行が複数ステップに渡る場合の検証
