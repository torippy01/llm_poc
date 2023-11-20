import os
from datetime import datetime
from typing import Optional

from langchain.agents import initialize_agent
from langchain.callbacks.base import BaseCallbackManager

from xecretary_core.agents.conf import Config
from xecretary_core.agents.mode import AgentExecutionMode
from xecretary_core.callback.callback import CustomCallbackHandler
from xecretary_core.evaluation.evaluation_sentences import EvaluateSentence
from xecretary_core.utils.utility import create_CBmemory, create_llm


class AgentRunner:
    def __init__(self, conf: Config):
        self.handler = CustomCallbackHandler(conf.generate_md_file())

        tools = conf.get_tools()
        llm = create_llm(conf.llm_name)
        memory = create_CBmemory()

        self.agent_executor = initialize_agent(
            agent=conf.agent_type,
            tools=tools,
            llm=llm,
            memory=memory,
            return_intermediate_steps=(
                conf.agent_type != "conversational-react-description"
            ),
            callback_manager=BaseCallbackManager([self.handler]),
        )

        self.eval_sentences_input_path = conf.eval_sentences_input_path
        self.eval_output_dir = conf.eval_output_dir
        self.agent_execution_mode = conf.agent_execution_mode

    def run(self) -> None:
        if self.agent_execution_mode == AgentExecutionMode.INTERACTIVE:
            self.run_agent_with_interactive()

        elif self.agent_execution_mode == AgentExecutionMode.QA:
            self.run_agent_with_Q_and_A()

        elif self.agent_execution_mode == AgentExecutionMode.SINGLE:
            self.run_agent_with_single_action()

        eval_output_path = os.path.join(
            self.eval_output_dir,
            datetime.utcfromtimestamp(int(datetime.now().timestamp())).strftime(
                "%Y%m%d_%H%M%S"
            )
            + ".yaml",
        )

        EvaluateSentence.from_list_to_yaml(
            self.handler.e_sentence_list, eval_output_path
        )

        self.handler.md_file.create_md_file()

    def run_agent_with_interactive(self) -> None:
        while True:
            print("feel free to ask me any questions. I'm here to help.")
            print("If you want to exit, just type 'exit'.")

            user_message = input()
            if user_message == "exit":
                break
            self.agent_executor({"input": user_message})

    def run_agent_with_Q_and_A(self) -> None:
        e_sentence_list = EvaluateSentence.from_yaml_to_list(
            self.eval_sentences_input_path
        )
        for e_sentence in e_sentence_list:
            self.agent_executor({"input": e_sentence.input})

    def run_agent_with_single_action(self, user_message=None) -> Optional[str]:
        if user_message:
            response = self.agent_executor({"input": user_message})
            return response.get("output", None)

        else:
            e_sentence = EvaluateSentence.from_yaml_to_list(
                self.eval_sentences_input_path
            )[0]
            self.agent_executor({"input": e_sentence.input})
