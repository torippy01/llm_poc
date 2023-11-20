from langchain.agents.agent_types import AgentType


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
        raise ValueError("Invalid value : 'agent_type_str'")
