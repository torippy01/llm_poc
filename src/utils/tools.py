from langchain.tools import tool
from llama_index.query_engine.retriever_query_engine import RetrieverQueryEngine
from dataclasses import dataclass
from typing import Callable


def command_predictor_wrapper(query_engine):
    # プロンプトから該当するAWSコマンドを推定するツール
    @tool
    def command_predictor(query: str):
        """
        AWS CLIコマンドを取得するツール
        """
        response = query_engine.query(query)
        return response.response
    
    return command_predictor


def parameter_predictor_wrapper(query_engine):
    # プロンプトからAWSコマンドの引数を推定するツール
    @tool
    def parameter_predictor(query: str):
        """
        AWS CLIコマンドの引数を取得するツール
        """
        response = query_engine.query(query)
        return response.response
    
    return parameter_predictor


def user_context_predictor_wrapper(query_engine):
    @tool
    def user_context_predictor(query: str):
        """
        ユーザーしか知らない知識を取得するツール
        """
        response = query_engine.query(query)
        return response.response

    return user_context_predictor


@dataclass
class CustomTool:
    query_engine: RetrieverQueryEngine
    command_predictor: Callable = command_predictor_wrapper
    parameter_predictor: Callable = parameter_predictor_wrapper
    user_context_predictor: Callable = user_context_predictor_wrapper
