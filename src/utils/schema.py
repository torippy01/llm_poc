from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Sequence
from langchain.schema import HumanMessage, AIMessage, AgentAction

@dataclass
class Experiment:
    md_filepath: str
    md_title: str
    tool_names: Union[List[str], str]
    llm: str
    user_index_dir: str
    aws_index_dir: str
    agent_type: str


@dataclass
class ConversationLog:
    input: str
    output: str
    intermediate_steps: Union[
        Sequence[AgentAction],
        Sequence[str],
        None
    ]
    chat_history: Union[
        List[HumanMessage],
        List[AIMessage],
        None
    ]
    elapsed_time: float


@dataclass
class EvaluateSentence:
    input: str
    output: str
    human_answer: Optional[str]
    evaluation: Optional[str]


class EvaluateSentences:
    def __init__(self):
        self.evaluation_sentences: List[EvaluateSentence] = []


    def append(self, evaluation_sentence: EvaluateSentence) -> None:
        self.evaluation_sentences.append(evaluation_sentence)


    def to_list(self) -> List[Dict[str, str]]:
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


    def to_yaml(self, yaml_filepath) -> None:
        import yaml
        listed_e = self.to_list()

        if len(listed_e) == 0:
            raise ValueError("評価すべき文章が登録されていません。")

        with open(yaml_filepath, "w") as f:
            yaml.dump(listed_e, f, allow_unicode=True)


    def __add__(self, other):
        if isinstance(other, EvaluateSentence):
            self.append(other)


class AgentConfig:
    def unpack(self):
        pass