from dataclasses import dataclass
from typing import List, Sequence, Union

from mdutils.mdutils import MdUtils

from langchain.schema import AgentAction, AIMessage, HumanMessage

from llama_index.response.schema import Response

from utils.utility import sep_md



@dataclass(frozen=True)
class ConversationLog:

    input: str
    output: str
    intermediate_steps: Union[Sequence[AgentAction], Sequence[str], None]
    chat_history: Union[List[HumanMessage], List[AIMessage], None]
    elapsed_time: float


    def dump(self, md_file: MdUtils) -> None:
        md_file.new_header(
            level=2, title=f"質問: {self.input}", add_table_of_contents="n"
        )

        md_file.new_line(f"実行時間: `{self.elapsed_time}`")

        if self.chat_history and self.intermediate_steps is None:
            for chat in self.chat_history:
                if isinstance(chat, HumanMessage):
                    md_file.new_line(f"human message: `{chat.content}`")
                if isinstance(chat, AIMessage):
                    md_file.new_line(f"AI message: `{chat.content}`")

        elif self.intermediate_steps:
            for step in self.intermediate_steps:
                (agent_action, answer) = step

                if isinstance(answer, Response):
                    answer = answer.response

                tool = agent_action.tool
                tool_input = agent_action.tool_input
                terminal_text = agent_action.log

                md_file.new_line(f"tool: `{tool}`")
                md_file.new_line(f"tool input: `{tool_input}`")
                md_file.new_line("log:")
                md_file.insert_code(terminal_text, language="bash")
                md_file.new_line("answer: ")
                md_file.insert_code(answer, language="bash")
                sep_md(md_file)

        md_file.new_line("final answer:")
        md_file.insert_code(self.output, language="bash")
        md_file.new_line()
        return