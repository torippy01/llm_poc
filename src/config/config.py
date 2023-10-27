from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Union

from mdutils.mdutils import MdUtils
import toml

from langchain.tools import BaseTool

from config.utils import get_cl_args_for_conf_toml
from tools.aws import CommandPredictorTool, ParameterPredictorTool
from tools.ht import create_HumanTool
from tools.shell import ShellAndSummarizeTool
from tools.uc import create_user_context_predictor_tool
from utils.utility import sep_md, Self


class AgentExecutionMode(Enum):
    """
    エージェントの実行方式を定義
    * QA
        - 事前に準備した問題集に対してエージェントが回答
        - 問題集を全て回答し次第、チェイン終了

    * INTERACTIVE
        - チャット形式で人間
        - 特定のキーワードを人間が入力し次第、チェイン終了

    * SINGLE
        - 単一の問に対してエージェントが回答
        - 回答し次第、チェイン終了
    """

    QA = auto()
    INTERACTIVE = auto()
    SINGLE = auto()

    @classmethod
    def from_str(cls, string: str) -> Union[Enum, None]:
        """
        列挙型の値に相当する文字列がある場合のみ`AgentExecutionMode`の列挙型データを返す．
        `string`の大文字・小文字は考慮しなくてよい．
        上記の条件に一致しない場合は全て`None`を返す．
        """
        if not string:
            return None

        string = string.upper()

        if string == cls.QA.name:
            return cls.QA

        elif string == cls.INTERACTIVE.name:
            return cls.INTERACTIVE

        elif string == cls.SINGLE.name:
            return cls.SINGLE

        else:
            return None


@dataclass(frozen=True)
class Config:

    agent_execution_mode: Enum
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

            elif tool_conf["name"] == "shell":
                tools.append(ShellAndSummarizeTool())

            elif tool_conf["name"] == "human":
                tools.append(create_HumanTool())

            else:
                tools.append(create_user_context_predictor_tool(tool_conf))

        if len(tools) == 0:
            raise RuntimeError("no tools are specified.")

        return tools


    def get_tools_names(self) -> str:
        return ", ".join([t["name"] for t in self.tools_conf])


    def generate_md_file(self) -> MdUtils:
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
    def fetch_config(cls) -> Self:
        args = get_cl_args_for_conf_toml()

        if args.conf_toml:
            with open(args.conf_toml, "r") as f:
                toml_data = toml.load(f)

            agent_execution_mode = AgentExecutionMode.from_str(
                string=toml_data.get("agent_execution_mode", "")
            )
            if agent_execution_mode is None:
                raise ValueError("agent_execution_modeの値が不正です")

            eval_sentences_path = toml_data.get("eval_sentence", None)

            # QA, Singleの場合、評価文は必須
            if agent_execution_mode in [AgentExecutionMode.QA, AgentExecutionMode.SINGLE] \
                and eval_sentences_path is None:
                raise RuntimeError(
                    f"agent_execution_modeを{AgentExecutionMode.QA.name}または"
                    "{AgentExecutionMode.SINGLE.name}とする場合はeval_sentences_path"
                    "を設定してください"
                )

            conf = Config(
                agent_execution_mode=agent_execution_mode,
                agent_type=toml_data.get("agent_type", "zero-shot-react-description"),
                llm_name=toml_data.get("llm", "gpt-4"),
                user_index_dir=toml_data.get("user_index_dir", "user_context_index"),
                pull=toml_data.get("pull", None),
                tools_conf=toml_data.get("tools_conf", {}),
                eval_sentences_path=eval_sentences_path,
                md_filepath=toml_data.get("md_filepath", "./repo/results/test.md"),
                md_title=toml_data.get("md_title", "TEST"),
            )

            return conf

        else:
            raise RuntimeError("Config TOML file is not found.")
