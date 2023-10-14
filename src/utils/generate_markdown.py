from typing import List

from langchain.schema import AIMessage, HumanMessage
from mdutils.mdutils import MdUtils

from utils.schema import ConversationLog, Experiment


def sep_md(mdFile: MdUtils) -> None:
    mdFile.new_line()
    mdFile.new_line("---")
    mdFile.new_line()


def _gen_md(mdFile: MdUtils, conversation_log: ConversationLog) -> None:
    mdFile.new_header(
        level=2, title=f"質問: {conversation_log.input}", add_table_of_contents="n"
    )

    mdFile.new_line(f"実行時間: `{conversation_log.elapsed_time}`")

    if conversation_log.chat_history and conversation_log.intermediate_steps is None:
        for chat in conversation_log.chat_history:
            if isinstance(chat, HumanMessage):
                mdFile.new_line(f"human message: `{chat.content}`")
            if isinstance(chat, AIMessage):
                mdFile.new_line(f"AI message: `{chat.content}`")

    elif conversation_log.intermediate_steps:
        for step in conversation_log.intermediate_steps:
            (agent_action, answer) = step

            tool = agent_action.tool
            tool_input = agent_action.tool_input
            terminal_text = agent_action.log

            mdFile.new_line(f"tool: `{tool}`")
            mdFile.new_line(f"tool input: `{tool_input}`")
            mdFile.new_line("log:")
            mdFile.insert_code(terminal_text, language="bash")
            mdFile.new_line("answer: ")
            mdFile.insert_code(answer, language="bash")
            sep_md(mdFile)

    mdFile.new_line("final answer:")
    mdFile.insert_code(conversation_log.output, language="bash")
    mdFile.new_line()


def gen_md(conversation_logs: List[ConversationLog], experiment: Experiment) -> None:
    mdFile = MdUtils(file_name=experiment.md_filepath, title=experiment.md_title)

    mdFile.new_line()
    mdFile.new_header(level=3, title="実験メタデータ", add_table_of_contents="n")
    mdFile.new_line()
    mdFile.new_list(
        [
            f"llm: `{experiment.llm_name}`",
            f"エージェントタイプ: `{experiment.agent_type}`",
            f"ユーザーコンテキスト: `{experiment.user_index_dir}`",
            f"ツール: `{experiment.tool_names}`",
        ]
    )

    sep_md(mdFile)

    for log in conversation_logs:
        _gen_md(mdFile, log)

    mdFile.create_md_file()
