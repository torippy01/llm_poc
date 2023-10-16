import asyncio
import subprocess
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import openai
from langchain.agents import load_tools
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import ShellTool
from langchain.tools.base import BaseTool
from llama_index.query_engine.retriever_query_engine import RetrieverQueryEngine

from utils.query_engines import get_query_engine
from utils.utility import get_llm


def get_aws_cli_version():
    aws_cli_version = (
        subprocess.check_output(["aws", "--version"]).decode("utf-8").strip()
    )

    return aws_cli_version


def get_gpt_response(query: str):
    response = (
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": query}]
        )
        .choices[0]["message"]["content"]
        .strip()
    )

    return response


class CommandPredictor(BaseTool):
    name = "command_predictor"
    description: str = f"""
        バージョン{get_aws_cli_version()}のAWS CLIコマンドを取得するツール
    """

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        return get_gpt_response(query)

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return await asyncio.get_event_loop().run_in_executor(
            None, get_gpt_response, query
        )


class ParameterPredictor(BaseTool):
    name = "command_predictor"
    description: str = f"""
        バージョン{get_aws_cli_version()}のAWS CLIコマンドの引数を取得するツール
    """

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        return get_gpt_response(query)

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        return await asyncio.get_event_loop().run_in_executor(
            None, get_gpt_response, query
        )


def user_context_predictor_wrapper(
    tool_name: str,
    query_engine: RetrieverQueryEngine,
    data_source: str,
):
    class UserContextPredictor(BaseTool):
        name = tool_name
        description: str = f"""
        ユーザーしか知らない知識を{data_source}から取得するツール
        """

        def _run(
            self,
            query: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
        ) -> str:
            return query_engine.query(query)

        async def _arun(
            self,
            query: str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        ) -> str:
            return await asyncio.get_event_loop().run_in_executor(
                None, query_engine.query, query
            )

    tool_instance = UserContextPredictor()
    return tool_instance


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


@dataclass(frozen=True)
class CustomTool:
    command_predictor: CommandPredictor = CommandPredictor()  # type: ignore
    parameter_predictor: ParameterPredictor = ParameterPredictor()  # type: ignore
    user_context_predictor: Callable = user_context_predictor_wrapper


def get_tools(tools_conf: List[Dict]):
    tools = list()

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
