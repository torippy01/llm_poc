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
### `llm` (Optional)
- エージェントがチェインで使用するLLM名
- 現在はOpenAI APIが提供するLLMのみ対応
- default `gpt-4`

### `user_index_dir` (Optional)
- ユーザーコンテキストのインデックスファイルのディレクトリを指定
- `storage/context`にインデックスファイルがあるとすれば、`storage`以下の値を設定（この場合`context`）
- default `user_context_index`

### `agent_type` (Optional)
- エージェントタイプを指定
- 下記から選択
  - zero-shot-react-description
  - conversational-react-description
  - chat-zero-shot-react-description
  - chat-conversational-react-description
- default `zero-shot-react-description`

### `agent_execution_mode` (Required)
- qa
  - 事前に準備した問題集にエージェントが回答

- interactive
  - チャット形式で人間
  - `exit`を入力後終了

- single
  - 単一の質問にエージェントが回答
  - 問題集を与えた場合は、最初の問のみ回答
  - `src.agents.agent`の`run_agent_with_interactive`メソッドに`user_message`を与えた場合は問題集より優先

### `eval_sentence` (Optional)
- 問題集のファイルパスを指定
- qaモードの場合は必要
- singleモードかつ`user_message`を与えない場合は必要

### `md_filepath` (Optional)
- 回答結果レポートのファイルパス
- default `./repo/results/test.md`

### `md_title` (Optional)
- 回答結果レポートのタイトル
- default `TEST`

### `tools_conf`
#### 事前定義ツール
* `name` (Required)
  - 下記のツール名を指定
    - command_predictor
    - parameter_predictor
    - shell
    - human
#### ユーザーコンテキストツール
* `name` (Required)
  - 任意のツール名を指定

* `index_dir` (Required)
  - ユーザーコンテキストのインデックスファイルを指定
  - `storage/context`にインデックスファイルがあるとすれば、`storage`以下の値を設定（この場合`context`）
* `data_source` (Required)
  - データソース名であり、ツールのディスクリプションに渡す情報
* `llm` (Required)
  - Llama Indexのクエリエンジンで使用するＬＬＭ名
  - 現在はOpenAI APIが提供するLLMのみ対応
