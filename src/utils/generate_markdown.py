from typing import Dict, List

from mdutils.mdutils import MdUtils
from utils.schema import Experiment



def sep_md(mdFile: MdUtils) -> None:
    mdFile.new_line()
    mdFile.new_line("---")
    mdFile.new_line()


def _gen_md(mdFile: MdUtils, result: Dict) -> None:
    question = result["response"]["input"]
    intermediate_steps = result["response"]["intermediate_steps"]
    final_answer = result["response"]["output"]
    elapsed_time = result["elapsed_time"]

    mdFile.new_header(
        level=2,
        title=f"質問: {question}",
        add_table_of_contents="n"
    )

    mdFile.new_line(f"実行時間: `{elapsed_time}`")

    for step in intermediate_steps:
        (agent_action, answer) = step

        tool = agent_action.tool
        tool_input = agent_action.tool_input
        log = agent_action.log

        mdFile.new_line(f"tool: `{tool}`")
        mdFile.new_line(f"tool input: `{tool_input}`")
        mdFile.new_line("log:")
        mdFile.insert_code(log, language="bash")
        mdFile.new_line("answer: ")
        mdFile.insert_code(answer, language="bash")
        sep_md(mdFile)
    mdFile.new_line("final answer:")
    mdFile.insert_code(final_answer, language="bash")
    mdFile.new_line()


def gen_md(results: List[Dict], experiment: Experiment) -> None:
    mdFile = MdUtils(
        file_name=experiment.md_filepath,
        title=experiment.md_title
    )

    mdFile.new_line()
    mdFile.new_header(
        level=3,
        title="実験メタデータ",
        add_table_of_contents="n"
    )
    mdFile.new_line()
    mdFile.new_list(
        [
            f"llm: `{experiment.llm}`",
            f"エージェントタイプ: `{experiment.agent_type}`",
            f"ユーザーコンテキスト: `{experiment.user_index_dir}`",
            f"AWSコンテキスト: `{experiment.aws_index_dir}`",
        ]
    )

    sep_md(mdFile)

    for result in results:
        _gen_md(mdFile, result)

    mdFile.create_md_file()