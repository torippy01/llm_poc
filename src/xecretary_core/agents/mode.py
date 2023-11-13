from typing import Optional

"""
エージェントの実行方式を定義
* QA
    - 事前に準備した問題集に対してエージェントが回答
    - 問題集を全て回答し次第、チェイン終了

* INTERACTIVE
    - チャット形式で人間
    - 特定のキーワードを人間が入力し次第、チェイン終了

* SINGLE
    - 単一の問に対してエージェントが回答
    - 回答し次第、チェイン終了
"""


class AgentExecutionMode:
    QA: str = "QA"
    INTERACTIVE: str = "INTERACTIVE"
    SINGLE: str = "SINGLE"

    @classmethod
    def from_str(cls, string: Optional[str]) -> Optional[str]:
        if string is None:
            return None

        string = string.upper()

        for mode in vars(cls):
            if string == mode:
                return string

        return None
