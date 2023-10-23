import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)
from langchain.tools import BaseTool

from llama_index.indices.query.base import BaseQueryEngine
from llama_index.llms.utils import LLMType
from llama_index import (
    LLMPredictor,
    ServiceContext,
    StorageContext,
    load_index_from_storage
)

from utils.utility import create_llm



def get_query_engine(
        index_dir: str,
        llm: Optional[LLMType]
    ) -> BaseQueryEngine:
    storage_dir = Path("./storage") / index_dir
    storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
    index = load_index_from_storage(storage_context, index_id=index_dir)
    llm_predictor = LLMPredictor(llm=llm)
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    return index.as_query_engine(service_context=service_context)



def create_user_context_predictor_tool(
        tool_conf: Dict[str, Any]
    ) -> BaseTool:
    llm = create_llm(tool_conf["llm"])
    query_engine = get_query_engine(tool_conf["index_dir"], llm)


    class UserContextPredictorTool(BaseTool):

        name: str = tool_conf["name"]
        description: str = f"""
        ユーザーしか知らない知識を{tool_conf["data_source"]}から取得するツール
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

    return UserContextPredictorTool()