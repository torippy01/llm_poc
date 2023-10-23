from typing import Dict, List

import yaml

from utils.schema import EvaluateSentence


class EvaluateSentences:
    def __init__(self):
        self.evaluation_sentences: List[EvaluateSentence] = []
        self.iter_cnt: int = 0

    def append(self, evaluation_sentence: EvaluateSentence) -> None:
        self.evaluation_sentences.append(evaluation_sentence)

    def from_yaml(self, yaml_filepath) -> None:
        with open(yaml_filepath) as f:
            listed_dict: List[Dict[str, str]] = yaml.safe_load(f)
        self.from_listed_dict(listed_dict)

    def from_listed_dict(self, listed_dict: List[Dict[str, str]]) -> None:
        if listed_dict is not None:
            for d in listed_dict:
                e_sentences = EvaluateSentence(
                    input=d["input"],
                    output=d["output"],
                    human_answer=d["human_answer"],
                    evaluation=d["evaluation"],
                )
                self.append(e_sentences)

    def to_yaml(self, yaml_filepath: str) -> None:
        listed_e = self.to_listed_dict()

        if len(listed_e) == 0:
            raise ValueError("評価すべき文章が登録されていません。")

        with open(yaml_filepath, "w") as f:
            yaml.dump(listed_e, f, allow_unicode=True)

    def to_listed_dict(self) -> List[Dict[str, str]]:
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
        if len(self.evaluation_sentences) == 0:
            return []
        _list = list()

        for e in self.evaluation_sentences:
            _list.append(
                {
                    "input": e.input,
                    "output": e.output,
                    "human_answer": e.human_answer,
                    "evaluation": e.evaluation,
                }
            )
        return _list

    def __add__(self, other: EvaluateSentence):
        if isinstance(other, EvaluateSentence):
            self.append(other)
        else:
            raise RuntimeError("EvaluateSentenceクラスのみ加算ができます")

    def __iter__(self):
        max_cnt: int = len(self.evaluation_sentences) - 1

        for i, e in enumerate(self.evaluation_sentences):
            if i > max_cnt:
                raise StopIteration()
            yield e
