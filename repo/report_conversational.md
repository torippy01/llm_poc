## 目的
様々な方法で対話的エージェントを実装し、それぞれの特性を調査

## 検証環境
### ChatGPT
* 推論用LLM: `gpt-4`

### Lang Chain
* エージェント：「調査項目」参照
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
  - `human`
    * Lang Chain公式ツール
    * 人間がAIのツールとして回答する世紀末ツール

### AWS
* XTERAプロジェクトのAWS環境にreadonlyのアカウントで実施

### Llama Index
* AWS CLIコマンドすべてのリファレンスを`GPTVectorStoreIndex`によってベクトル変換したインデックスを使用

## 検証方法
* 対話的なエージェントタイプに質問文を投げかけてみる
* Humanツールを様々なエージェントタイプに試す

### 質問文
* 対話的エージェントは、「ユーザーコンテキストを参照」するのか、また「ユーザーへ質問すべき事項を質問する」のかを検証するため、以下の目的をもった質問文を準備
  - ユーザーの補助を必要とする質問
    `プロジェクトリーダーの名前ってなんでしたっけ？`
  - ユーザーコンテキストを必要とする質問
    `いつも開発で使っているインスタンスは今稼働してますか？`

## 検証結果と所見
* [zero-shot-react-description × Human as a Tool](./results/conversational/zeroshot_human.md)
* [conversational-react-description](./results/conversational/conv_react.md)
* [conversational-react-description × Human as a Tool](./results/conversational/conv_react_human.md)
* [chat-zero-shot-react-description](./results/conversational/chat_zeroshot.md)
* [chat-zero-shot-react-description × Human as a Tool](./results/conversational/chat_zeroshot_human.md)
* [chat-conversational-react-description](./results/conversational/chat_conv.md)
* [chat-conversational-react-description × Human as a Tool](./results/conversational/chat_conv_human.md)
* [hwchase17/react-chat](./results/conversational/hwchase17_react-chat.md)


## まとめと感想
### 全般
* 各エージェントタイプで同一の質問をした結果、次のような印象を受けた．
  - AWSコマンドを使用する質問は、いずれのエージェントも等しく回答できた．
  - ユーザーコンテキストに含まれない情報に関する質問では、エージェント毎に特色があることが分かった．

### エージェントタイプの性能評価
* `zero-shot-react-description × Human as a Tool`の組み合わせの特性
  - 手持ちのツールで懸命に情報を取得しようとする．
  - 回答に資する情報が見当たらない場合は、humanツールを最終手段として使用する印象
  - 結論、この組み合わせが最も信頼できそうな感覚でいる．

* `conversational-*`のエージェントタイプの特性
  - プライバシーに関する情報は提供しない．
  - 質問に対する完全な回答が得られない場合でも、これを最終回答とする傾向がある．
  - 対話を通じてユーザーから必要な情報を聞き出すような動き．

* `chat-*`と`hwchase17/react-chat`のエージェントタイプの特性
  - ツールによる推論で所望の情報が得られない場合は「わかりません」といった回答を行う傾向がある(humanツールがあまり機能しない)．


### Agentの出力解析の失敗について
* LangChainでは、Agent Action毎にエージェントが最終的にはじき出したテキストを解析する．
* 解析では、主にプレフィックスの値をチェックする．このプレフィックスにより、チェインを継続するか、ユーザーへの回答を完了するかを判断する．
  - プレフィックスの例（`Final Answer`、`thought`、`Observation`）
* 今回試したものの内、`zero-shot-react-description`と`hwchase17/react-chat`以外のものは出力解析に失敗することがしばしば起きる．
* 「重要！`thought`の後は必ず`Agent Input`か`Final Answer`のプレフィックスをつけてください。」といったプロンプトに書き換えるとうまくいくといった報告がなされてる．
