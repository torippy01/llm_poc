## 目的
- AWS CLIによるコマンド及びオプションの推論を安定させる方法を検証
- Chat GPTにAWS CLIコマンドを推論させる

## 検証環境
### ChatGPT
* 推論用LLM: `gpt-4`

### Lang Chain
* エージェント：`zero-shot-react-description`
* ツール
  - `command_predictor_beta`
    * Chat GPT APIで実装
    * 特定のAWS CLIのバージョンのコマンドを取得するツール
  - `parameter_predictor_beta`
    * Chat GPT APIで実装
    * 特定のAWS CLIのバージョンのコマンド引数を取得するツール
  - `user_context_predictor`
    * Llama Indexで実装(`GPTVectorStoreIndex`)
    * ユーザーしか知らない知識を取得するツール
  - `shell_tool`
    * Lang Chain公式ツール
    * コマンドをターミナル上で実行するツール
  - `human`
    * Lang Chain公式ツール
    * 人間がAIのツールとして回答する世紀末ツール

* 実行コマンド
  ```
  python src/validate.py -q eval_sentence/indexless_predictor.yaml \
    --md-filepath repo.md --md-title Indexless \
    --tools command_predictor_beta \
      parameter_predictor_beta \
      user_context_predictor \
      shell_tool human
  ```

### AWS
* XTERAプロジェクトのAWS環境にreadonlyのアカウントで実施

## 検証方法
* 過去のベンチマークで用いた質問文に加え、より複雑な要求を行う．
* `command_predictor_beta`と`parameter_predictor_beta`
  - 動的に取得したAWS CLIのバージョンをディスクリプションに付与
  - チェイン中に渡されるクエリを`gpt-3.5-turbo`にPOSTし、その回答をツールのレスポンスとする．

## 検証結果
[結果レポート](./results/indexless.md)

## まとめと感想
* AWSコマンドの索引精度が上昇
* 過去試した質問集を変わらぬ精度で回答可能
* AWSコマンドのためのLlama Indexのクエリエンジンを整備する必要無し
* ある程度高度な質問に対しても筋道立てて実行しようとしている．
  - ssh接続に必要な情報を探す
  - 必要に応じてbash / pythonを使用
* 一部、インスタンスのリージョンなどコマンドでわかることをユーザーコンテキストから探そうとするなどの挙動が見られた．
