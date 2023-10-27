## 設定ファイルの例

```toml
llm = "gpt-4"
user_index_dir = "user_context_index"
agent_type = "zero-shot-react-description"
agent_execution_mode = "qa"
eval_sentence = "eval_sentence/test_ai_answer.yaml"
md_filepath = "./repo/results/test.md"
md_title = "TEST"

[[tools_conf]]
name = "command_predictor"

[[tools_conf]]
name = "parameter_predictor"

[[tools_conf]]
name = "shell"

[[tools_conf]]
name = "human"

[[tools_conf]]
name = "user_context_predictor"
index_dir = "user_context_index"
data_source = "document"
llm = "gpt-3.5-turbo"
```

## 設定項目の説明
* `llm`
  - エージェントがチェインで使用するLLM名
  - 現在はOpenAI APIが提供するLLMのみ対応

* `user_index_dir`
  - ユーザーコンテキストのインデックスファイルのディレクトリを指定
  - `storage/context`にインデックスファイルがあるとすれば、`storage`以下の値を設定（この場合`context`）

* `agent_type`
  - エージェントタイプを指定
  - 下記から選択
    - zero-shot-react-description
    - conversational-react-description
    - chat-zero-shot-react-description
    - chat-conversational-react-description

* `agent_execution_mode`
  - QA (qa)
      - 事前に準備した問題集に対してエージェントが回答
      - 問題集を全て回答し次第、チェイン終了

  - INTERACTIVE (interactive)
      - チャット形式で人間
      - 特定のキーワードを人間が入力し次第、チェイン終了

  - SINGLE (single)
      - 単一の問に対してエージェントが回答
      - 回答し次第、チェイン終了

* `eval_sentence`
  - 問題集のファイルパスを指定

* `md_filepath`
  - 問題集の回答結果レポートのファイルパス

* `md_title`
  - 問題集の回答結果レポートのタイトル

* `tools_conf`
  - 下記のツールを指定可能
    - command_predictor
    - parameter_predictor
    - shell
    - human
    - 任意の名前のツール（ただし、ユーザーコンテキスト検索の用途に限る）※
  - ※のツール以外は`name`のみ設定
  - ※のツール以下の項目を設定
    - `name`: ツール名
    - `index_dir`: ユーザーコンテキストのインデックスファイルを指定
      - `storage/context`にインデックスファイルがあるとすれば、`storage`以下の値を設定（この場合`context`）
    - `data_source`: データソース名．ツールのディスクリプションに渡す情報
    - `llm`: Llama Indexのクエリエンジンで使用するＬＬＭ名
      - 現在はOpenAI APIが提供するLLMのみ対応
