from dataclasses import dataclass
from typing import List, Optional

import toml

from langchain.agents.agent_types import AgentType
from langchain.tools import BaseTool
from mdutils.mdutils import MdUtils

from xecretary_core.agents.mode import AgentExecutionMode
from xecretary_core.agents.utils import agent_types_from_string
from xecretary_core.tools.conf import ToolConfig
from xecretary_core.utils.utility import Self, sep_md


@dataclass(frozen=True)
class Config:
    agent_execution_mode: str
    agent_type: AgentType
    llm_name: str
    user_index_dir: str
    pull: str
    tool_confs: List[ToolConfig]
    eval_sentences_input_path: Optional[str]
    eval_output_dir: str
    md_filepath: str
    md_title: str

    def get_tools(self) -> List[BaseTool]:
        tools = [tool_conf.get_tool() for tool_conf in self.tool_confs]
        if len(tools) == 0:
            raise RuntimeError("Config error : set 'tool_confs'")
        return tools

    def get_name_of_tools(self) -> str:
        return ", ".join([tool_conf.name for tool_conf in self.tool_confs])

    def generate_md_file(self) -> MdUtils:
        # TODO: markdownファイルを生成していないので、関数名を変更すべき
        md_file = MdUtils(file_name=self.md_filepath, title=self.md_title)

        md_file.new_line()
        md_file.new_header(level=3, title="実験メタデータ", add_table_of_contents="n")
        md_file.new_line()

        tools_name = self.get_name_of_tools()
        md_file.new_list(
            [
                f"llm: `{self.llm_name}`",
                f"エージェントタイプ: `{self.agent_type}`",
                f"ユーザーコンテキスト: `{self.user_index_dir}`",
                f"ツール: `{tools_name}`",
            ]
        )
        sep_md(md_file)
        return md_file

    @classmethod
    def fetch(cls, toml_path: Optional[str]) -> Self:
        if toml_path is None:
            raise ValueError("Invalid value : 'toml_path'")

        with open(toml_path, "r") as f:
            toml_data = toml.load(f)

        agent_execution_mode = AgentExecutionMode.from_str(
            toml_data.get("agent_execution_mode", None)
        )

        if agent_execution_mode is None:
            raise ValueError("Config error : set 'agent_execution_mode'")

        eval_sentences_input_path = None
        if agent_execution_mode in (AgentExecutionMode.QA, AgentExecutionMode.SINGLE):
            eval_sentences_input_path = toml_data.get("eval_sentence", None)
            if eval_sentences_input_path is None:
                raise ValueError("Config error : set 'eval_sentence'")

        agent_type = agent_types_from_string(
            toml_data.get("agent_type", "zero-shot-react-description")
        )

        eval_output_dir = toml_data.get("eval_output", "var/eval_sentence/result/")

        conf = Config(
            agent_execution_mode=agent_execution_mode,
            agent_type=agent_type,
            llm_name=toml_data.get("llm", "gpt-4"),
            user_index_dir=toml_data.get("user_index_dir", "user_context_index"),
            pull=toml_data.get("pull", None),
            tool_confs=ToolConfig.fetch(toml_data.get("tools_conf", {})),
            eval_sentences_input_path=eval_sentences_input_path,
            eval_output_dir=eval_output_dir,
            md_filepath=toml_data.get("md_filepath", "./repo/results/test.md"),
            md_title=toml_data.get("md_title", "TEST"),
        )

        return conf
