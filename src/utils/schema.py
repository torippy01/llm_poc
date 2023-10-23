from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Union

from langchain.chat_models import ChatOpenAI
from langchain.schema import AgentAction, AIMessage, BaseMemory, HumanMessage
from langchain.tools import BaseTool


# エージェントを構成するパラメータをもつデータクラス

@dataclass
class ToolConf:
    name: str
    index_dir: str
    llm: Optional[ChatOpenAI]
    data_source: str


@dataclass(frozen=True)
class Config:
    interactive: bool
    agent_type: str
    llm_name: str
    user_index_dir: str
    pull: str
    tool_conf: Dict
    eval_sentences: str
    md_filepath: str
    md_title: str


@dataclass(frozen=True)
class Experiment:
    md_filepath: str
    md_title: str
    tool_names: Union[List[str], str]
    llm_name: str
    user_index_dir: str
    agent_type: str


@dataclass(frozen=True)
class AgentExecutorConfig:
    llm: ChatOpenAI
    tools: List[BaseTool]
    memory: BaseMemory
    agent_type: str
    pull: str
    interactive: bool
    eval_sentences: str
    experiment: Experiment

@dataclass(frozen=True)
class ConversationLog:
    input: str
    output: str
    intermediate_steps: Union[Sequence[AgentAction], Sequence[str], None]
    chat_history: Union[List[HumanMessage], List[AIMessage], None]
    elapsed_time: float


@dataclass
class EvaluateSentence:
    input: str
    output: str
    human_answer: Optional[str]
    evaluation: Optional[str]
