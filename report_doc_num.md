## 目的
インデックス化する文量がLlama IndexとLang Chainに対して与える影響を検証します．

## 検証環境
### ChatGPT
* モデル：`gpt-3.5-turbo`

### Lang Chain
* エージェント：`zero-shot-react-description`
* ツール
  - `command_predictor`
    * Llama Indexで実装
    * ユーザーの要望を満たすAWSコマンドを表示します．
  - `parameter_predictor_from_query`
    * Llama Indexで実装
    * ユーザーの質問文中から、AWSコマンドに必要な引数を抽出して表示します．引数が見つからない場合は、ユーザーに引数が見当たらない旨を通知します．

### Llama Index
* インデックス化手法：`GPTVectorStoreIndex`

## 検証手法
* AWS CLIのサブコマンドdescribe-instancesの[公式ドキュメント](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instances.html)を基準の文量とし、これを１単位とする．
* １単位は1300行程度
* １単位をインデックス化した場合と、５単位をインデックス化した場合において下記の変化を検証する．
  - 同一の質問を10回実施したときの実行時間
  - 主観による対話の精度
  - openaiの料金


## 検証結果
### 実行時間
#### １単位の場合
* 平均
* 分散

#### ５単位の場合
* 平均
* 分散

---
### 主観による対話の精度
#### １単位の場合
* 質問
* 回答

#### ５単位の場合
* 質問
* 回答

---
### openaiの料金

---
## その他
* [ソースコード](./validate_single_document.py)
