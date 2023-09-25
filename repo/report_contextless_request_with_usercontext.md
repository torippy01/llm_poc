## 目的
ユーザーコンテキストを考慮するエージェントに対して、コンテキスト情報を必要としない質問を与えた場合の挙動を検証する．

## 検証環境
[コンテキストつきの自然言語からAWS CLIのコマンドを実行させる検証](./repo/report_exec_command_context.md)(以下「前回の検証」)に同じ．

## 検証手法
* 検証コードの実行コマンド
  ```bash
  streamlit run src/validate_exec_command_contextless.py
  ```
* ユーザーコンテキストを考慮するエージェントに対し、前回の検証で行った質問を再度行う．
* 前回の検証で得た回答と比較し、回答精度に影響が及んでいるかを確認

## 検証結果
* [検証結果](./results/result_contextless_using_usercontext.md)

## まとめと感想
### 全般
* 正答率の低下が確認
* すべての質問において、`command_predictor`が機能していないことを確認
* AWSコマンドはChat GPTの知識を使っている　⇒　期待する挙動ではない．
* 「項目Examplesのコマンド実行結果が答え」と誤認するケースが散見
  - やはり前処理はちゃんとやったほうがよさそう…
  - それでもだめならツールのディスクリプションを再検討すべき

### 感想
* リファレンスの前処理によって`command_predictor`及び`parameter_predictor_from_query`の精度向上が確認できるかが気になる．
* ツールを追加した際は、前まで異常のないツールであっても回答の品質に影響がないかチェックする必要があると感じた．検証結果レポートを作成するコストを減らすために、あらかじめ準備した質問集と、AIの回答のログを自動で収集するツールを開発したほうがよさそうな気がしている．