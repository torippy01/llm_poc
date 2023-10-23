from langchain.memory import ConversationBufferMemory

from agents.agent_executor import CustomAgentExecutor
from utils.config_parser import get_conf
from utils.schema import AgentExecutorConfig, Experiment
from tools.get_tools import get_tools
from utils.utility import get_llm


def main(conf):
    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        output_key="output",
    )

    tools = get_tools(conf.tool_conf)
    tool_names = ", ".join([t["name"] for t in conf.tool_conf])

    llm = get_llm(conf.llm_name)

    experiment = Experiment(
        md_filepath=conf.md_filepath,
        md_title=conf.md_title,
        tool_names=tool_names,
        llm_name=conf.llm_name,
        user_index_dir=conf.user_index_dir,
        agent_type=conf.agent_type
    )

    agent_executor_conf = AgentExecutorConfig(
        llm=llm,
        tools=tools,
        memory=memory,
        agent_type=conf.agent_type,
        pull=conf.pull,
        interactive=conf.interactive,
        eval_sentences=conf.eval_sentences,
        experiment=experiment
    )

    agent_executor = CustomAgentExecutor(agent_executor_conf)
    e_sentences = agent_executor.run()

    e_sentences.to_yaml(yaml_filepath=conf.eval_sentences)


if __name__ == "__main__":
    conf = get_conf()
    main(conf)
