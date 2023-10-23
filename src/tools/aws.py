import asyncio
from typing import Optional
import subprocess

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
from langchain.tools import BaseTool

from utils.utility import get_gpt_response



def get_aws_cli_version() -> str:
    return subprocess.check_output(["aws", "--version"]).decode("utf-8").strip()


class CommandPredictorTool(BaseTool):
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



class ParameterPredictorTool(BaseTool):
    name = "parameter_predictor"
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