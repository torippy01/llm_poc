from typing import List, Optional, Tuple

import yaml
from langchain import hub
from langchain.agents import AgentExecutor, initialize_agent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers.react_single_input import \
    ReActSingleInputOutputParser
from langchain.tools.render import render_text_description

from utils.evaluation_sentences import EvaluateSentences
from utils.schema import AgentExecutorConfig, ConversationLog, EvaluateSentence
from utils.utility import time_measurement


# AgentExecutorConfigからAgentExecutorを生成するクラス
class CustomAgentExecutor:
    def __init__(self, conf: AgentExecutorConfig) -> None:
        self.conf = conf

        if conf.pull:
            prompt = hub.pull(conf.pull)
            prompt = prompt.partial(
                tools=render_text_description(conf.tools),
                tool_names=", ".join([t.name for t in conf.tools]),
            )

            llm_with_stop = conf.llm.bind(stop=["\nObservation"])

            agent = (
                {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_log_to_str(
                        x["intermediate_steps"]
                    ),
                    "chat_history": lambda x: x["chat_history"],
                }
                | prompt
                | llm_with_stop
                | ReActSingleInputOutputParser()
            )

            self.agent_executor = AgentExecutor(
                agent=agent, tools=conf.tools, verbose=True, memory=conf.memory
            )

        else:
            return_intermediate_steps = (
                False
                if conf.agent_type in ["conversational-react-description"]
                else True
            )

            self.agent_executor = initialize_agent(
                agent=conf.agent_type,
                tools=conf.tools,
                llm=conf.llm,
                memory=conf.memory,
                verbose=True,
                return_intermediate_steps=return_intermediate_steps,
            )

    def run(self):
        return AgentRunner(
            agent_executor=self.agent_executor,
            is_interactive=self.conf.interactive,
            eval_sentences=self.conf.eval_sentences,
        ).run()


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

    def run(self) -> Tuple[List[ConversationLog], EvaluateSentences]:
        if self.is_interactive:
            return self.run_agent_with_interactive()
        else:
            return self.run_agent_with_Q_and_A()

    def run_agent_with_interactive(
        self,
    ) -> Tuple[List[ConversationLog], EvaluateSentences]:
        conversation_log = list()
        e_sentences = EvaluateSentences()

        while True:
            print("AIへのメッセージを書いてください。\n" "終了する場合は'exit'と入力してください。")

            user_message = input()
            if user_message == "exit":
                break

            response, elapsed_time = time_measurement(
                self.agent_executor.invoke, {"input": {"input": user_message}}
            )

            conversation_log.append(
                ConversationLog(
                    input=response.get("input"),
                    output=response.get("output"),
                    intermediate_steps=response.get("intermediate_steps", None),
                    chat_history=response.get("chat_history", None),
                    elapsed_time=elapsed_time,
                )
            )

            e_sentences.append(
                EvaluateSentence(
                    input=response.get("input"),
                    output=response.get("output"),
                    human_answer=None,
                    evaluation=None,
                )
            )
        return conversation_log, e_sentences

    def run_agent_with_Q_and_A(self) -> Tuple[List[ConversationLog], EvaluateSentences]:
        conversation_log = list()
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
            response, elapsed_time = time_measurement(
                self.agent_executor.invoke, {"input": {"input": user_message}}
            )

            conversation_log.append(
                ConversationLog(
                    input=response.get("input"),
                    output=response.get("output"),
                    intermediate_steps=response.get("intermediate_steps", None),
                    chat_history=response.get("chat_history", None),
                    elapsed_time=elapsed_time,
                )
            )

            e_sentences.append(
                EvaluateSentence(
                    input=response.get("input"),
                    output=response.get("output"),
                    human_answer=sentences["human_answer"],
                    evaluation=None,
                )
            )
        return conversation_log, e_sentences
