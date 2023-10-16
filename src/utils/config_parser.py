"""
コマンドライン引数またはTOMLファイルをパースし、Configオブジェクトとして返します.
"""

import argparse
import os

import openai
import toml
from dotenv import load_dotenv

from utils.schema import Config


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf-toml", type=str, help="設定TOMLファイルを指定します．")
    return parser.parse_args()


def get_conf():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    args = get_args()

    if args.conf_toml is not None:
        with open(args.conf_toml, "r") as f:
            toml_data = toml.load(f)

        conf = Config(
            interactive=toml_data.get("interactive", False),
            agent_type=toml_data.get("agent_type", "zero-shot-react-description"),
            llm_name=toml_data.get("llm", "gpt-4"),
            user_index_dir=toml_data.get("user_index_dir", "user_context_index"),
            pull=toml_data.get("pull", None),
            tool_conf=toml_data.get("tools_conf", {}),
            eval_sentences=toml_data.get(
                "eval_sentence", "eval_sentence/test_ai_answer.yaml"
            ),
            md_filepath=toml_data.get("md_filepath", "./repo/results/test.md"),
            md_title=toml_data.get("md_title", "TEST"),
        )

        return conf

    else:
        raise RuntimeError("TOML設定ファイルが見つかりません。")
