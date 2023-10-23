from dataclasses import dataclass
from typing import Dict, List

from mdutils.mdutils import MdUtils
import toml

from langchain.tools import BaseTool

from config.utils import get_CL_args_for_conf_toml
from tools.aws import CommandPredictorTool, ParameterPredictorTool
from tools.ht import CreateHumanTool
from tools.shell import ShellAndSummarizeTool
from tools.uc import CreateUserContextPredictorTool
from utils.utility import sep_md, Self



@dataclass(frozen=True)
class Config:

    is_interactive: bool
    agent_type: str
    llm_name: str
    user_index_dir: str
    pull: str
    tools_conf: Dict[str, str]
    eval_sentences_path: str
    md_filepath: str
    md_title: str


    def get_tools(self) -> List[BaseTool]:
        tools : List[BaseTool] = list()

        for tool_conf in self.tools_conf:
            if tool_conf["name"] == "command_predictor":
                tools.append(CommandPredictorTool())

            elif tool_conf["name"] == "parameter_predictor":
                tools.append(ParameterPredictorTool())

            if tool_conf["name"] == "shell":
                tools.append(ShellAndSummarizeTool())

            elif tool_conf["name"] == "human":
                tools.append(CreateHumanTool())

            else:
                tools.append(CreateUserContextPredictorTool(tool_conf))

        if len(tools) == 0:
            raise RuntimeError("no tools are specified.")

        return tools


    def get_tools_names(self) -> str:
        return ", ".join([t["name"] for t in self.tools_conf])


    def generate_md_file(self) -> None:
        md_file = MdUtils(file_name=self.md_filepath, title=self.md_title)

        md_file.new_line()
        md_file.new_header(level=3, title="実験メタデータ", add_table_of_contents="n")
        md_file.new_line()

        tools_name = self.get_tools_names()
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
    def fetch_config(self) -> Self:
        args = get_CL_args_for_conf_toml()

        if args.conf_toml:
            with open(args.conf_toml, "r") as f:
                toml_data = toml.load(f)

            conf = Config(
                is_interactive=toml_data.get("interactive", False),
                agent_type=toml_data.get("agent_type", "zero-shot-react-description"),
                llm_name=toml_data.get("llm", "gpt-4"),
                user_index_dir=toml_data.get("user_index_dir", "user_context_index"),
                pull=toml_data.get("pull", None),
                tools_conf=toml_data.get("tools_conf", {}),
                eval_sentences_path=toml_data.get("eval_sentence", "eval_sentence/test_ai_answer.yaml"),
                md_filepath=toml_data.get("md_filepath", "./repo/results/test.md"),
                md_title=toml_data.get("md_title", "TEST"),
            )

            return conf

        else:
            raise RuntimeError("Config TOML file is not found.")