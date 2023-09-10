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
streamlit run <pythonファイル名>
```

## 検証レポート
* [文量がインデックス化に与える影響の検証](./report_doc_num.md)(検証中)
* Google検索によりAWSコマンドを推定させる検証 (未検証)
