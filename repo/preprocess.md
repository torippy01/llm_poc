## 目的
AWS CLIリファレンスのノイズを削除した場合における対話精度を検証する．

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
* AWS CLIリファレンスから、コマンドのディスクリプション、文法、引数、出力に関する記述のみを抽出した文書を作成
* この文書を`GPTVectorStoreIndex`を用いてインデックス化

## 検証手法
* 検証コードの実行コマンド
  ```bash
  python src/validate.py --aws-index-dir aws_ref --questions repo/questions/q1.txt
  ```
* リファレンスを前処理したインデックスを用いて質問を行う．
* 質問は「コンテキストつき」「コンテキストなし」の両方で実施

## 検証結果
* [結果レポート](./results/preprocess.md)

## まとめと感想
### `command_predictor`及び`parameter_predictor_from_query`の回答精度が若干向上
* 以前の検証では「バックアップ」や「running」等の語彙から、用例のテキストにひっぱられた回答をすることはなくなった．

### 気になったところ
* `describe-instances`の実行を期待しているが、`list-instances`を実行しようとしているものもあった（`instance`と名のつくコマンドが361個存在する割に正確、と言えばそうとも思える…）．
* `GPTVectorStoreIndex`以外の[インデックス化手法](https://gpt-index.readthedocs.io/en/stable/core_modules/data_modules/index/index_guide.html)も注目すべきな気がする．
  - ユーザーコンテキストから特定のキーワードを検索（例えばインスタンスID）するとき、[Keyword Table Index](https://gpt-index.readthedocs.io/en/stable/core_modules/data_modules/index/index_guide.html#keyword-table-index)を使うと相性良いのではないか？
  - ユーザーコンテキストに階層化されたデータ（例えばjson）を持つならば、[Tree Index](https://gpt-index.readthedocs.io/en/stable/core_modules/data_modules/index/index_guide.html#tree-index)が相性が良いのではないか？
* プロンプトにテンプレを仕込む方法も気になる．
  - [Llama Indexにテンプレートを仕込む方法](https://gpt-index.readthedocs.io/en/stable/examples/customization/prompts/completion_prompts.html)
  - [Lang Chainのエージェントにテンプレートを仕込む方法](https://book.st-hakky.com/docs/langchain-custom-agent/)


### 今後の検証・検討の方向性
- 他のインデックス化手法を試してみる．
- Prompt Templateを編集して回答精度が上がるか試す．
- AIの答えを評価する方法を模索する．