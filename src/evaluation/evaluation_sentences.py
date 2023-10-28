from dataclasses import dataclass
from typing import Dict, List, Optional

import yaml

from utils.utility import Self, get_gpt_response


@dataclass
class EvaluateSentence:
    input: str
    output: str
    human_answer: Optional[str]
    evaluation: Optional[str]

    def evaluate(self) -> None:
        content = f"""
            回答文は、質問文に対する回答が書かれています。
            評価文に基づいて、回答文の評価を行いなさい．
            評価は、１から３の３段階評価とします。
            評価のフォーマットは、`評価：評価数`とします。
            また、なぜその評価を行ったかを説明しなさい。

            質問文： {self.input}
            回答文： {self.output}
            評価文： {self.human_answer}
        """

        self.evaluation = get_gpt_response(content)
        return

    def to_dict(self) -> Dict[str, Optional[str]]:
        e_dict = {
            "input": self.input,
            "output": self.output,
            "human_answer": self.human_answer,
            "evaluation": self.evaluation,
        }
        return e_dict

    @classmethod
    def from_dict(self, e_dict: Dict[str, Optional[str]]) -> Self:
        e_sentences = EvaluateSentence(
            input=e_dict["input"],
            output=e_dict["output"],
            human_answer=e_dict["human_answer"],
            evaluation=e_dict["evaluation"],
        )
        return e_sentences

    @classmethod
    def from_yaml_to_list(self, yaml_filepath: Optional[str]) -> List[Self]:
        if yaml_filepath is None:
            raise RuntimeError("no file is specified.")
        with open(yaml_filepath) as f:
            listed_dict = yaml.safe_load(f)

        if listed_dict is not None:
            return [self.from_dict(e_dict) for e_dict in listed_dict]
        else:
            raise RuntimeError("no sentences to evaluate in file")

    @classmethod
    def from_list_to_yaml(
        self, e_sentences_list: List[Self], yaml_filepath: str
    ) -> None:
        """
        以下のリストデータに変換
        [
            {
                "input": <人間の入力>,
                "output": <エージェントの最終出力>,
                "human_answer": <人間が用意した模範解答>,
                "evaluation": <outputの評価値>
            }, {...}
        ]
        """

        dict_list = list()
        for e_sentences in e_sentences_list:
            dict_list.append(e_sentences.to_dict())

        if len(dict_list) == 0:
            raise ValueError("評価すべき文章が登録されていません。")

        with open(yaml_filepath, "w") as f:
            yaml.dump(dict_list, f, allow_unicode=True)
        return
