from typing import List

from langchain import hub
from langchain.agents import AgentExecutor, initialize_agent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.tools.render import render_text_description

from config.config import Config
from conv_log.conv_log import ConversationLog
from evaluation.evaluation_sentences import EvaluateSentence
from utils.utility import create_CBmemory, create_llm, time_measurement



class AgentRunner:


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

        if conf.is_interactive is None:
            self.is_interactive = False
        else:
            self.is_interactive = conf.is_interactive

        if self.is_interactive:
            self.eval_sentences_path = None
        else:
            if conf.eval_sentences_path is None:
                raise RuntimeError("問題集のファイルパスが指定されていません")
            self.eval_sentences_path = conf.eval_sentences_path

        self.md_file = conf.generate_md_file()


    def run(self) -> None:
        if self.is_interactive:
            e_sentences_list = self.run_agent_with_interactive()
        else:
            e_sentences_list = self.run_agent_with_Q_and_A()
        if self.eval_sentences_path:
            EvaluateSentence.from_list_to_yaml(e_sentences_list, self.eval_sentences_path)

        self.md_file.create_md_file()
        return


    def run_agent_with_interactive(self) -> List[EvaluateSentence]:
        e_sentences_list = list()

        while True:
            print("AIへのメッセージを書いてください。")
            print("終了する場合は'exit'と入力してください。")

            user_message = input()
            if user_message == "exit":
                break

            response, elapsed_time = time_measurement(
                self.agent_executor.invoke,
                {"input": {"input": user_message}}
            )

            conversation_log = ConversationLog(
                input=response.get("input"),
                output=response.get("output"),
                intermediate_steps=response.get("intermediate_steps", None),
                chat_history=response.get("chat_history", None),
                elapsed_time=elapsed_time,
            )
            conversation_log.dump(self.md_file)

            e_sentences_list.append(
                EvaluateSentence(
                    input=response.get("input"),
                    output=response.get("output"),
                    human_answer=None,
                    evaluation=None,
                )
            )
            print(response.get("output"))

        return e_sentences_list


    def run_agent_with_Q_and_A(self) -> list[EvaluateSentence]:
        e_sentences_list = EvaluateSentence.from_yaml_to_list(self.eval_sentences_path)
        for e_sentences in e_sentences_list:
            response, elapsed_time = time_measurement(
                self.agent_executor.invoke, {"input": {"input": e_sentences.input}}
            )

            conversation_log = ConversationLog(
                input=response.get("input"),
                output=response.get("output"),
                intermediate_steps=response.get("intermediate_steps", None),
                chat_history=response.get("chat_history", None),
                elapsed_time=elapsed_time,
            )
            conversation_log.dump(self.md_file)

            e_sentences.output = response.get("output")
            # e_sentences.evaluate()

        return e_sentences_list
