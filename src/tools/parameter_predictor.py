import asyncio

from langchain.tools.base import BaseTool
from tools.utils import get_aws_cli_version, get_gpt_response
from typing import Optional
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

class ParameterPredictor(BaseTool):
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
