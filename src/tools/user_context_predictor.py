from llama_index.query_engine.retriever_query_engine import RetrieverQueryEngine
from typing import Optional
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool


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