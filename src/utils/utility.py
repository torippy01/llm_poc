import time
from typing import Any, Callable
from langchain.chat_models import ChatOpenAI


def time_measurement(func: Callable, val: Any) -> Any:
    start = time.time()
    response = func(**val)
    elapsed_time = time.time() - start
    return response, elapsed_time


def get_llm(llm: str) -> ChatOpenAI:
    return ChatOpenAI(temperature=0, model_name=llm)