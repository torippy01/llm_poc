from langchain import hub
from langchain.agents import AgentExecutor, initialize_agent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers.react_single_input import (
    ReActSingleInputOutputParser,
)
from langchain.callbacks.base import BaseCallbackManager
from langchain.tools.render import render_text_description
from agents.agent_runner import AgentRunner
from utils.schema import AgentExecutorConfig


# AgentExecutorConfigからAgentExecutorを生成するクラス
class CustomAgentExecutor:
    def __init__(self, conf: AgentExecutorConfig) -> None:
        self.conf = conf
        # 現コードではhubの内容がpromptを前提としている
        # TODO pullした内容を判別してAgentに組み込む修正
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
                agent=agent,
                tools=conf.tools,
                verbose=True,
                memory=conf.memory,
                handle_parsing_errors=True,
            )

        else:

            return_intermediate_steps = (
                False
                if conf.agent_type in ["conversational-react-description"]
                else True
            )

            from utils.callback_handler import CustomCallbackHandler

            handler = CustomCallbackHandler()
            handler.experiment = conf.experiment
            callback_manager = BaseCallbackManager(handlers=[handler])

            self.agent_executor = initialize_agent(
                agent=conf.agent_type,
                tools=conf.tools,
                llm=conf.llm,
                memory=conf.memory,
                verbose=True,
                return_intermediate_steps=return_intermediate_steps,
                callback_manager=callback_manager,
            )

    def run(self):
        return AgentRunner(
            agent_executor=self.agent_executor,
            is_interactive=self.conf.interactive,
            eval_sentences=self.conf.eval_sentences,
        ).run()
