from typing import List, Optional

from langchain import hub
from langchain.agents import AgentExecutor, initialize_agent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.tools.render import render_text_description

from config.config import Config
from conv_log.conv_log import ConversationLog
from evaluation.evaluation_sentences import EvaluateSentence
from utils.utility import create_CBmemory, create_llm, time_measurement
from config.config import AgentExecutionMode


class AgentRunner:

    # hub.pull()の結果がpromptを前提としているが、実際はその限りでない
    # TODO: hub.pullの結果を判別してagentに適用するよう修正
    def __init__(self, conf: Config):
        llm = create_llm(conf.llm_name)
        memory = create_CBmemory()
        tools = conf.get_tools()

        if conf.pull:
            prompt = hub.pull(conf.pull)
            prompt = prompt.partial(
                tools=render_text_description(tools),
                tool_names=conf.get_tools_names(),
            )

            llm_with_stop = llm.bind(stop=["\nObservation"])

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

            self.agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory)

        else:
            ri_steps = conf.agent_type not in ["conversational-react-description"]

            self.agent_executor = initialize_agent(
                agent=conf.agent_type,
                tools=tools,
                llm=llm,
                memory=memory,
                return_intermediate_steps=ri_steps,
            )

        self.eval_sentences_path = conf.eval_sentences_path
        self.agent_execution_mode = conf.agent_execution_mode
        self.e_sentences_list = list()
        self.md_file = conf.generate_md_file()


    def run(self) -> None:
        if self.agent_execution_mode == AgentExecutionMode.INTERACTIVE:
            self.run_agent_with_interactive()

        elif self.agent_execution_mode == AgentExecutionMode.QA:
            self.run_agent_with_Q_and_A()

        elif self.agent_execution_mode == AgentExecutionMode.SINGLE:
            self.run_agent_with_single_action()

        if self.eval_sentences_path:
            EvaluateSentence.from_list_to_yaml(
                self.e_sentences_list,
                self.eval_sentences_path
            )

        self.md_file.create_md_file()


    def update_conversation_log(self):
        conversation_log = ConversationLog(
            input=self.response.get("input"),
            output=self.response.get("output"),
            intermediate_steps=self.response.get("intermediate_steps", None),
            chat_history=self.response.get("chat_history", None),
            elapsed_time=self.elapsed_time,
        )
        conversation_log.dump(self.md_file)


    def update_eval_sentences_list(self):
        self.e_sentences_list.append(
            EvaluateSentence(
                input=self.response.get("input"),
                output=self.response.get("output"),
                human_answer=None,
                evaluation=None,
            )
        )


    def run_agent_with_interactive(self) -> None:
        while True:
            print("AIへのメッセージを書いてください。")
            print("終了する場合は'exit'と入力してください。")

            user_message = input()
            if user_message == "exit":
                break

            self.response, self.elapsed_time = time_measurement(
                self.agent_executor.invoke,
                {"input": {"input": user_message}}
            )

            self.update_conversation_log()
            self.update_eval_sentences_list()


    def run_agent_with_Q_and_A(self) -> None:
        e_sentences_list = EvaluateSentence.from_yaml_to_list(self.eval_sentences_path)
        for e_sentences in e_sentences_list:
            self.response, self.elapsed_time = time_measurement(
                self.agent_executor.invoke, {"input": {"input": e_sentences.input}}
            )
            self.update_conversation_log()
            self.update_eval_sentences_list()


    def run_agent_with_single_action(
        self,
        user_message: Optional[str] = None
    ) -> None:
        """
        user_messageが引数として渡された場合はその値をエージェントの
        入力とする．
        ない場合は`eval_sentences_path`の記述の先頭だけ処理する．
        """

        if user_message:
            self.response, self.elapsed_time = time_measurement(
                self.agent_executor.invoke,
                {"input": {"input": user_message}}
            )
            self.update_conversation_log()
            self.update_eval_sentences_list()

        else:
            e_sentences = EvaluateSentence.from_yaml_to_list(
                self.eval_sentences_path
            )[0]
            self.response, self.elapsed_time = time_measurement(
                self.agent_executor.invoke,
                {"input": {"input": e_sentences.input}}
            )
            self.update_conversation_log()
            self.update_eval_sentences_list()
