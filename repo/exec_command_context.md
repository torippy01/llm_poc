## 目的
開発用AWS環境において、ユーザーの自然言語から所望のコマンドを実行させることができるかを検証する．
当検証においては、案件やプロダクトに関するコンテキストを考慮する．

## 検証環境
### ChatGPT
* 推論用LLM: `gpt-4`

### Lang Chain
* エージェント：`zero-shot-react-description`
* ツール
  - `command_predictor`
    * Llama Indexで実装
    * AWS CLIコマンドを取得するツール
  - `parameter_predictor_from_prompt`
    * Llama Indexで実装
    * AWS CLIコマンドの引数を取得するツール
  - `user_context_predictor`
    * Llama Indexで実装
    * ユーザーしか知らない知識を取得するツール
  - `shell_tool`
    * Lang Chain公式ツール
    * コマンドをターミナル上で実行するツール

### AWS
* XTERAプロジェクトのAWS環境にreadonlyのアカウントで実施

### Llama Index
* AWS CLIコマンドすべてのリファレンスを`GPTVectorStoreIndex`によってベクトル変換したインデックスを使用

## 検証手法
* 検証コードの実行コマンド
  ```bash
  streamlit run src/validate_exec_command_context.py
  ```
* AWSのインデックスとは別に、ユーザーのコンテキストのインデックスを用意（以下ユーザーコンテキスト）
* `user_context_predictor`ツールはユーザーコンテキストを使用
* ユーザーコンテキストに関する質問及び、ユーザーコンテキストを用いてAWSコマンドを実行させる質問を実施
* 各推論モデルの回答を分析

## 検証結果
* 検証結果（質問回答集）は別途配布（セキュリティの事由から）

## まとめと感想
### 案件固有の質問に対する回答について
* 「開発人数は？」「プロジェクト名は？」等案件固有の質問に対する回答は正確
* インデックスを「AWS CLI用」と「ユーザーコンテキスト用」に分けたことが功を成したか．

### コンテキスト情報を用いたAWSコマンドの実行について
* 概ね正確な回答を行っていた．
* AWSコマンドの引数の部分を、ユーザーコンテキストを参照して取得できる点を確認
* `user_context_predictor`ツールを導入後、`command_predictor`や`parameter_predictor_from_prompt`のツールが推論を正しく行わないケースが見られた．
  - OpenAIの知識を使ってコマンド実行する例が多数みられた．
  - 質問４の誤答は、`optworks describe-instances`の[用例結果](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/opsworks/describe-instances.html#examples)を索引したものと思料
  - 用例などコマンドの文法に直接関係のないテキストは推論精度に悪影響？
  - 「リファレンスのテキストを前処理」 or 「manコマンドをインデックス化」など必要最小限のテキストをインデックス化したほう良い？
  - ツール導入による精度劣化の原因は正直よくわからない．

* プロンプトの書き方１つでAIの回答が変わる．
  - 「バックアップ用のインスタンス」⇒　誤答
  - 「バックアップ用のEC2インスタンス」⇒　正答
  - 「EC2」をつけると正解することから、多少は具体性をもって書くとよさそう．

### 今後の検証・検討の方向性
  - ドキュメントの前処理方法の検討
  - 入力トークン数が多い場合の対処法の検討
  - 多量のAWS CLIインデックスの扱い方の検討
  - コマンド実行が複数ステップに渡る場合の検証

## 注
検証用スクリプトは現在存在しない