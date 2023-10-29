from typing import Dict, List, Optional

from langchain.tools import BaseTool

# from tools.tool_aws import CommandPredictorTool, ParameterPredictorTool
from tools.tool_human import create_HumanTool
from tools.tool_shell import ShellAndSummarizeTool
from tools.tool_uc_predictor import create_user_context_predictor_tool
from utils.utility import Self



class ToolConfig:

    def __init__(self, dc: Dict[str, Optional[str]]):
        self.name: str = dc["name"]
        self.index_dir: Optional[str] = dc.get("index_dir")
        self.data_source: Optional[str] = dc.get("data_source")
        self.llm_name: Optional[str] = dc.get("llm")


    def get_tool(self) -> BaseTool:
        # if self.name == "command_predictor":
            # return CommandPredictorTool()
        # elif self.name == "parameter_predictor":
            # return ParameterPredictorTool()
        if self.name == "shell":
            return ShellAndSummarizeTool()
        elif self.name == "human":
            return create_HumanTool()
        else:
            return create_user_context_predictor_tool(
                self.name,
                self.index_dir,
                self.data_source,
                self.llm_name
            )

    @classmethod
    def fetch(
        cls,
        dc_list: List[Dict[str, Optional[str]]]
    ) -> List[Self]:

        return [ToolConfig(dc) for dc in dc_list]