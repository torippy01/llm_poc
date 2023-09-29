from dataclasses import dataclass
from typing import List


@dataclass
class Experiment:
    md_filepath: str
    md_title: str
    tool_names: List[str]
    llm: str
    user_index_dir: str
    aws_index_dir: str
    agent_type: str
