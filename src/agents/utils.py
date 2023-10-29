from typing import Any

from langchain import hub
from langchain.agents.agent_types import AgentType
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.chat_models.base import BaseChatModel



# hub.pull()の結果がpromptを前提としているが、実際はその限りでない
# TODO: hub.pullの結果を判別してagentに適用するよう修正

def fetch_agent_from_hub(
    pull,
    llm: BaseChatModel,
    tool_description: str,
    tool_names: str
) -> Any:

    ## need to modify
    prompt = hub.pull(pull)
    prompt = prompt.partial(
        tools=tool_description,
        tool_names=tool_names,
    )

    return (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_str(
                x["intermediate_steps"]
            ),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm.bind(stop=["\nObservation"])
        | ReActSingleInputOutputParser()
    )


def agent_types_from_string(agent_type_str: str) -> AgentType:
    agent_type_str = agent_type_str.upper().replace("-", "_")

    if agent_type_str == AgentType.ZERO_SHOT_REACT_DESCRIPTION.name:
        return AgentType.ZERO_SHOT_REACT_DESCRIPTION

    elif agent_type_str == AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION.name:
        return AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION

    elif agent_type_str == AgentType.SELF_ASK_WITH_SEARCH.name:
        return AgentType.SELF_ASK_WITH_SEARCH

    elif agent_type_str == AgentType.REACT_DOCSTORE.name:
        return AgentType.REACT_DOCSTORE

    elif agent_type_str == AgentType.OPENAI_MULTI_FUNCTIONS.name:
        return AgentType.OPENAI_MULTI_FUNCTIONS

    elif agent_type_str == AgentType.OPENAI_FUNCTIONS.name:
        return AgentType.OPENAI_FUNCTIONS

    elif agent_type_str == AgentType.CONVERSATIONAL_REACT_DESCRIPTION.name:
        return AgentType.CONVERSATIONAL_REACT_DESCRIPTION

    elif agent_type_str == AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION.name:
        return AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION

    elif agent_type_str == AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION.name:
        return AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION

    else:
        raise ValueError("Invalid value : agent_type_str")

