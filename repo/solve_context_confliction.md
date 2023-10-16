## 目的
- ユーザーコンテキストに矛盾する状況が予測されており、この場合のエージェントの挙動がどうなるか未知数
- 当検証では矛盾を作為し、最終的に正しい情報を使ったオペレーションを行うための足掛かりを模索していく．

## 検証環境
### ChatGPT
* 推論用LLM: `gpt-4`

### Lang Chain
* エージェント：`zero-shot-react-description`
* ツール
  - 「検証手法」参照

## 検証
### ドキュメント
以下の２パターンのドキュメントを使用

1. 「[ドキュメント](../user_context/conflict_doc/context.md)」「[チャット履歴](../user_context/correct_chat/context.md)」間で矛盾が生ずるパターン
    * ドキュメントとチャットの内容で、「本番運用ＥＣ２インスタンスＩＤ」に矛盾があるようにする．
    * チャット履歴の方がTrue

2. チャット履歴内で矛盾が生ずるパターン
    * チャット履歴内で、「本番運用ＥＣ２インスタンスＩＤ」に矛盾があるようにする．
    * 新しい方がtrue
    * タイムスタンプが[あるもの](../user_context/conflict_chat/context.md)と[ないもの](../user_context/conflict_chat_timestampless/context.md)の２種類

3. [ドキュメントにチャット履歴を含めるパターン](../llm_poc/user_context/union_doc_chat/context.md)
    * チャット履歴の方がTrue

### 検証１
* `document_user_context_predictor`ツールと`chat_user_context_predictor`ツールの２つを実装する．チャットの方がTrueの情報をもつ．
* 検証コマンド
  ```
  python src/validate.py --conf-toml conf/two_tool_two_con.toml
  ```
* [検証結果](./results/conflict/two_tools_two_context.md)

### 検証２

* `user_context_predictor`にドキュメント・チャット履歴の内容をまとめて持たせる．
* 検証コマンド
  ```
  python src/validate.py --conf-toml conf/single_tool_union_context.toml
  ```
* [検証結果](./results/conflict/single_tool_union_context.md)

### 検証３

* `user_context_predictor`に誤った／正確なIDの両方をもつチャット履歴を持たせる．タイムスタンプは**付与する**．
* 実行コマンド
  ```
  python src/validate.py --conf-toml conf/single_tool_conflict_chat.toml
  ```
* [検証結果](./results/conflict/single_tool_conflict_chat.md)

### 検証４

* `user_context_predictor`に誤った／正確なIDの両方をもつチャット履歴を持たせる．タイムスタンプは**付与しない**．
* 実行コマンド
  ```
  python src/validate.py --conf-toml conf/single_tool_conflict_chat_timestampless.toml
  ```
* [検証結果](./results/conflict/single_tool_conflict_chat_timestampless.md)

---

## まとめと感想
### 各検証所見
* 検証１では、たまたま正確な結果が得られたが、勝率は５割
* 検証２では、コンテキストを混合するのはNGであることを示せた．
* 検証３では、時系列を加味して正確なIDを抜き出せることが示せた．コンテキストは分離すべきと思料
* 検証４では、タイムスタンプの有無がチャット履歴参照の精度に影響を与えないことが分かった．チャットの文脈では下の行の方が時系列的に最近であるとLLMが理解しているためか？

### ツール分離・統合、どっちがよい？
* 検証２の結果から、ツール分離が吉．

### ツール分離で誤るケースをどう対処するか？
* ユーザーコンテキストのケース毎にエージェントを分け、エージェント間で協議することで解決できないか？
* 複数エージェントをどう分けるべきかは要議論．以下のエージェントを提案
  - オーガナイザーエージェント
    * 各エージェントにタスクを振る
    * ユーザーコンテキストから複数の情報を抽出するように指示
    * ユーザーコンテキストから得られた情報のうち、確からしい情報をエンジニアエージェント、またはユーザーに提供する
  - エンジニアエージェント
    * コマンドの実行類を担当
  - コンサルティングエージェント
    * ユーザーコンテキストの抽出を担当
    * コンテキストドメイン（Google Drive, Github, Chat tool, etc.）毎にエージェントを配置

### その他対処すべき事項
* インスタンスが４つに増えた影響で、コマンド結果取得時にトークン超過が発生
* 対処の方法を議論したい．
* APIの実装はこの問題を対処してから行いたい．

## 実行コマンド
### インデックス作成コマンド
* ドキュメント(誤り)
  ```
  python src/utils/create_user_index.py \
    --index-id conflict_doc \
    --context-dir user_context/conflict_doc
  ```

* チャット(正解)
  ```
  python src/utils/create_user_index.py \
    --index-id correct_chat \
    --context-dir user_context/correct_chat
  ```


* ドキュメント・チャット混合
  ```
  python src/utils/create_user_index.py \
    --index-id union_doc_chat \
    --context-dir user_context/union_doc_chat
  ```

* チャット内矛盾(タイムスタンプあり)
  ```
  python src/utils/create_user_index.py \
    --index-id conflict_chat \
    --context-dir user_context/conflict_chat
  ```

* チャット内矛盾(タイムスタンプなし)
  ```
  python src/utils/create_user_index.py \
    --index-id conflict_chat_timestampless \
    --context-dir user_context/conflict_chat_timestampless
  ```
