from typing import Optional

from langchain.agents import AgentExecutor, initialize_agent
from langchain.callbacks.base import BaseCallbackManager
from langchain.tools.render import render_text_description

from agents.conf import Config
from agents.mode import AgentExecutionMode
from agents.utils import fetch_agent_from_hub
from callback.callback import CustomCallbackHandler
from evaluation.evaluation_sentences import EvaluateSentence
from utils.utility import create_CBmemory, create_llm



class AgentRunner:

    def __init__(
        self,
        conf: Config
    ):

        self.handler = CustomCallbackHandler(conf.generate_md_file())

        tools = conf.get_tools()
        llm = create_llm(conf.llm_name)
        memory = create_CBmemory()

        if conf.pull:
            self.agent_executor = AgentExecutor(
                agent=fetch_agent_from_hub(
                    pull=conf.pull,
                    llm=llm,
                    tool_description=render_text_description(tools),
                    tool_names=conf.get_name_of_tools()
                ),
                tools=tools,
                memory=memory,
                callback_manager=BaseCallbackManager([self.handler])
            )

        else:
            self.agent_executor = initialize_agent(
                agent=conf.agent_type,
                tools=tools,
                llm=llm,
                memory=memory,
                return_intermediate_steps=(
                    conf.agent_type != "conversational-react-description"
                ),
                callback_manager=BaseCallbackManager([self.handler])
            )

        self.eval_sentences_path = conf.eval_sentences_path
        self.agent_execution_mode = conf.agent_execution_mode


    def run(self) -> None:
        if self.agent_execution_mode == AgentExecutionMode.INTERACTIVE:
            self.run_agent_with_interactive()

        elif self.agent_execution_mode == AgentExecutionMode.QA:
            self.run_agent_with_Q_and_A()

        elif self.agent_execution_mode == AgentExecutionMode.SINGLE:
            self.run_agent_with_single_action()

        else:
            raise RuntimeError(
                f"Invalid agent_execution_mode : {self.agent_execution_mode}"
            )

        if self.eval_sentences_path:
            EvaluateSentence.from_list_to_yaml(
                self.handler.e_sentence_list,
                self.eval_sentences_path
            )

        self.handler.md_file.create_md_file()
        return


    def run_agent_with_interactive(self) -> None:
        while True:
            print("AIへのメッセージを書いてください。")
            print("終了する場合は'exit'と入力してください。")

            user_message = input()
            if user_message == "exit":
                return
            self.agent_executor({"input": user_message})


    def run_agent_with_Q_and_A(self) -> None:
        e_sentence_list = EvaluateSentence.from_yaml_to_list(self.eval_sentences_path)
        for e_sentence in e_sentence_list:
            self.agent_executor(input={"input": e_sentence.input})
        return


    def run_agent_with_single_action(
        self,
        user_message: Optional[str] = None
    ) -> Optional[str]:
        """
        user_messageが引数として渡された場合はその値をエージェントの
        入力とする．
        ない場合は`eval_sentences_path`の記述の先頭だけ処理する．
        """

        if user_message:
            response = self.agent_executor(input={"input": user_message})
            return response.get("output", None)

        else:
            if not self.eval_sentences_path:
                raise RuntimeError("回答すべき質問が見当たりませんでした")

            e_sentence = EvaluateSentence.from_yaml_to_list(self.eval_sentences_path)[0]
            self.agent_executor(input={"input": e_sentence.input})
            return
