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
* ⌨ 全文書をインデックス化した場合の検証
* 🔜 コンテキストのインデックス化方法の検証
* 🔜 コンテキストつきの自然言語からAWS CLIのコマンドを実行させる検証
* 🔜 コマンド実行が複数ステップに渡る場合の検証
