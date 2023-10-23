from typing import Optional

import yaml
from langchain.agents import AgentExecutor

from evaluation.evaluation_sentences import EvaluateSentences
from utils.schema import EvaluateSentence
from utils.utility import time_measurement



# AgentExecutorを実行するクラス
class AgentRunner:
    def __init__(
        self,
        agent_executor: AgentExecutor,
        is_interactive: bool,
        eval_sentences: Optional[str],
    ) -> None:
        self.agent_executor = agent_executor
        self.is_interactive = is_interactive if is_interactive is not None else False

        # インタラクティブモードの場合は問題集は不要
        if self.is_interactive:
            self.eval_sentence = None

        # インタラクティブモードでない場合は問題集は必須
        else:
            if eval_sentences is None:
                raise RuntimeError("問題集のファイルパスが指定されていません")
            self.eval_sentences = eval_sentences


    def run(self) -> EvaluateSentences:
        if self.is_interactive:
            return self.run_agent_with_interactive()
        else:
            return self.run_agent_with_Q_and_A()


    def run_agent_with_interactive(
        self,
    ) -> EvaluateSentences:
        e_sentences = EvaluateSentences()

        while True:
            print(
                "AIへのメッセージを書いてください。\n"
                "終了する場合は'exit'と入力してください。"
            )

            user_message = input()
            if user_message == "exit":
                break
            response = self.agent_executor.invoke(input={"input": user_message})

            e_sentences.append(
                EvaluateSentence(
                    input=response.get("input"),
                    output=response.get("output"),
                    human_answer=None,
                    evaluation=None,
                )
            )
        return  e_sentences


    def run_agent_with_Q_and_A(self) -> EvaluateSentences:
        e_sentences = EvaluateSentences()

        # QAのyamlファイルをオープン
        if self.eval_sentences is None:
            raise RuntimeError("問題集のファイルパスが指定されていません")

        with open(self.eval_sentences) as f:
            eval_sentences = yaml.safe_load(f)

        # 質問群に対してエージェントが回答
        # 回答結果をQAに追加
        for sentences in eval_sentences:
            user_message = sentences["input"]
            response, _ = time_measurement(
                self.agent_executor.invoke, {"input": {"input": user_message}}
            )

            e_sentences.append(
                EvaluateSentence(
                    input=response.get("input"),
                    output=response.get("output"),
                    human_answer=sentences["human_answer"],
                    evaluation=None,
                )
            )
        return e_sentences
