## 目的
エージェントに対して質問をした際に、エージェントが持ちえない情報を対話的に与える方法を調査する．

## 調査項目
### Agent Type
* [zero-shot-react-description](https://python.langchain.com/docs/modules/agents/agent_types/#zero-shot-react)
  - [ReActフレームワーク](https://book.st-hakky.com/docs/llm-prompt-engineering-react/#react-%E3%81%AE%E6%A6%82%E8%A6%81)を使用
  - ツールのディスクリプションのみに基づいて使用するツールを決定
  - Human as a Toolを併用することでエージェントに対話性を持たせられそう

* [conversational-react-description](https://python.langchain.com/docs/modules/agents/agent_types/#conversational)
  - エージェントが積極的に人間と対話するようにチューニングされたエージェントタイプ
  - ReActフレームワークを使用
  - Memoryを使用し、以前の会話のやり取りを記憶

* chat-zero-shot-react-description
  - 公式サイトの説明がなく、詳細は不明

* chat-conversational-react-description
  - 公式サイトの説明がなく、詳細は不明

### Tools
* Human as a Tool
  - 人間がツールとして（世紀末を感じる）エージェントを補助
  - エージェントが解を見いだせず、混乱しているときに使用
  - エージェントの質問を人間の回答し、これをツールの出力とする

### Callback Handler
* [HumanApprovalCallbackHandler](https://python.langchain.com/docs/modules/agents/tools/human_approval)
  - エージェントのツール使用を都度人間に承認を求める．
  - 例えば、ShellToolにこのコールバックハンドラを指定すると、シェル実行を人間の許可なしに実行しないようになる．


### LangChain Hub
* [hwchase17/react-chat](https://smith.langchain.com/hub/hwchase17/react-chat)
  - 積極的に対話を行う
  - 幅広いタスクをこなす
