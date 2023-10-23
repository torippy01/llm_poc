from typing import Dict, List

from langchain.agents import load_tools
from langchain.agents.agent import ExceptionTool
from langchain.tools import ShellTool
from tools.schema import CustomTool

from index.query_engines import get_query_engine
from utils.utility import get_llm


def get_input():
    print(
        "Insert your text. Enter 'q' or press Ctrl-D (or Ctrl-Z on Windows) " "to end."
    )
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "q":
            break
        contents.append(line)
    return "\n".join(contents)


def get_tools(tools_conf: List[Dict]):
    tools = list()
    default_tool = [ExceptionTool()]
    tools.extend(default_tool)

    for conf in tools_conf:
        if "command_predictor" == conf["name"]:
            tools.append(CustomTool.command_predictor)

        elif "parameter_predictor" == conf["name"]:
            tools.append(CustomTool.parameter_predictor)

        elif "shell" in conf["name"]:
            tools.append(ShellTool())

        elif "human" in conf["name"]:
            tools.append(load_tools(["human"], input_func=get_input)[0])

        else:
            llm = get_llm(conf["llm"])
            query_engine = get_query_engine(conf["index_dir"], llm)
            tools.append(
                CustomTool.user_context_predictor(
                    tool_name=conf["name"],
                    query_engine=query_engine,
                    data_source=conf["data_source"],
                )
            )

    if len(tools) == 0:
        raise RuntimeError("ツールが指定されていません．")

    return tools
