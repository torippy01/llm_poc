from enum import Enum, auto
from typing import TypedDict, Union


class ToolConfig(TypedDict):
    name: str
    index_dir: Union[str, None]
    data_source: Union[str, None]
    llm: Union[str, None]


class AgentExecutionMode(Enum):
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

    QA = auto()
    INTERACTIVE = auto()
    SINGLE = auto()

    @classmethod
    def from_str(cls, string: str) -> Union[Enum, None]:
        """
        列挙型の値に相当する文字列がある場合のみ`AgentExecutionMode`の列挙型データを返す．
        `string`の大文字・小文字は考慮しなくてよい．
        上記の条件に一致しない場合は全て`None`を返す．
        """
        if not string:
            return None

        string = string.upper()

        if string == cls.QA.name:
            return cls.QA

        elif string == cls.INTERACTIVE.name:
            return cls.INTERACTIVE

        elif string == cls.SINGLE.name:
            return cls.SINGLE

        else:
            return None