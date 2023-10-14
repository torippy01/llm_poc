"""
python src/validate.py \
    --agent-type chat-zero-shot-react-description \
    --interactive
"""

from langchain.memory import ConversationBufferMemory

from utils.agents import CustomAgentExecutor
from utils.config_parser import get_conf
from utils.generate_markdown import gen_md
from utils.schema import AgentExecutorConfig, Experiment
from utils.tools import get_tools
from utils.utility import get_llm


def main(conf):
    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        output_key="output",
    )

    tools = get_tools(conf.tool_conf)
    print(tools)
    llm = get_llm(conf.llm_name)

    agent_executor_conf = AgentExecutorConfig(
        llm=llm,
        tools=tools,
        memory=memory,
        agent_type=conf.agent_type,
        pull=conf.pull,
        interactive=conf.interactive,
        eval_sentences=conf.eval_sentences,
    )

    agent_executor = CustomAgentExecutor(agent_executor_conf)
    conversation_log, e_sentences = agent_executor.run()

    experiment = Experiment(
        md_filepath=conf.md_filepath,
        md_title=conf.md_title,
        tool_names=", ".join([tool_name for tool_name in conf.tool_names]),
        llm_name=conf.llm_name,
        user_index_dir=conf.user_index_dir,
        agent_type=conf.agent_type,
    )

    gen_md(
        conversation_logs=conversation_log,
        experiment=experiment,
    )

    e_sentences.to_yaml(yaml_filepath=conf.eval_sentences)


if __name__ == "__main__":
    conf = get_conf()
    main(conf)
