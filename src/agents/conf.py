from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import toml

from langchain.agents.agent_types import AgentType
from langchain.tools import BaseTool
from mdutils.mdutils import MdUtils

from agents.mode import AgentExecutionMode
from agents.utils import agent_types_from_string
from tools.conf import ToolConfig
from utils.utility import Self, sep_md



@dataclass(frozen=True)
class Config:

    agent_execution_mode: str
    agent_type: AgentType
    llm_name: str
    user_index_dir: str
    pull: str
    tool_confs: List[ToolConfig]
    eval_sentences_input_path: Optional[str]
    eval_sentences_output_path: str
    md_filepath: str
    md_title: str


    def get_tools(self) -> List[BaseTool]:
        tools = [tool_conf.get_tool() for tool_conf in self.tool_confs]
        if len(tools) == 0:
            raise RuntimeError("no tools are specified.")
        return tools


    def get_name_of_tools(self) -> str:
        return ", ".join([tool_conf.name for tool_conf in self.tool_confs])


    def generate_md_file(self) -> MdUtils:
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
    def fetch(
        cls,
        toml_path: Optional[str]
    ) -> Self:

        if toml_path is None:
            raise RuntimeError("Config TOML file is not found.")

        with open(toml_path, "r") as f:
            toml_data = toml.load(f)

        agent_execution_mode = AgentExecutionMode.from_str(
            toml_data.get("agent_execution_mode", "")
        )

        if agent_execution_mode is None:
            raise ValueError("Invalid value : agent_execution_mode")

        eval_sentences_input_path = None
        if agent_execution_mode == AgentExecutionMode.QA:
            eval_sentences_input_path = toml_data.get("eval_sentence", None)
            if eval_sentences_input_path is None:
                raise ValueError(
                    f"agent_execution_modeを{AgentExecutionMode.QA.name}に指定した場合は"
                    "eval_sentenceを設定してください"
                )

        agent_type = agent_types_from_string(
            toml_data.get("agent_type", "zero-shot-react-description")
        )

        default_output_path = "eval_sentence/result/" + datetime.utcfromtimestamp(
            int(datetime.now().timestamp())
        ).strftime('%Y%m%d_%H%M%S') + ".yaml"

        conf = Config(
            agent_execution_mode=agent_execution_mode,
            agent_type=agent_type,
            llm_name=toml_data.get("llm", "gpt-4"),
            user_index_dir=toml_data.get("user_index_dir", "user_context_index"),
            pull=toml_data.get("pull", None),
            tool_confs=ToolConfig.fetch(toml_data.get("tools_conf", {})),
            eval_sentences_input_path=eval_sentences_input_path,
            eval_sentences_output_path=toml_data.get("eval_output", default_output_path),
            md_filepath=toml_data.get("md_filepath", "./repo/results/test.md"),
            md_title=toml_data.get("md_title", "TEST"),
        )

        return conf

