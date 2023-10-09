"""
python src/validate.py \
    --agent-type chat-zero-shot-react-description \
    --interactive
"""

import argparse
import os
import openai

from dotenv import load_dotenv

from langchain.agents import load_tools
from langchain.chat_models import ChatOpenAI
from langchain.tools import ShellTool
from langchain.memory import ConversationBufferMemory

from utils.generate_markdown import gen_md
from utils.schema import Experiment
from utils.tools import CustomTool
from utils.query_engines import get_query_engine
from utils.agents import AgentExecutorConfig, AgentExecutorGen, AgentRunner


def set_config():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--llm",
        type=str,
        default="gpt-4",
        help="推論用LLM名を指定します。"
    )
    parser.add_argument(
        "--aws-index-dir",
        type=str,
        default="aws_ref",
        help="AWSインデックスのJsonファイルのディレクトリ名を指定します。"
    )
    parser.add_argument(
        "--user-index-dir",
        type=str,
        default="user_context_index",
        help="ユーザーインデックスのJsonファイルのディレクトリ名を指定します。"
    )
    parser.add_argument(
        "--agent-type",
        type=str,
        default="zero-shot-react-description",
        choices=[
            "zero-shot-react-description",
            "conversational-react-description",
            "react-docstore",
            "self-ask-with-search",
            "chat-zero-shot-react-description",
            "chat-conversational-react-description",
            "structured-chat-zero-shot-react-description",
            "openai-functions",
            "openai-multi-functions",
        ],
        help="エージェントのタイプを指定します。"
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="指定した場合、インタラクティブモードで実行します。",
    )
    parser.add_argument(
        "-q",
        "--qa",
        default="qa/test.yaml",
        type=str,
        help="質問回答集のファイルパスを指定します。"
    )
    parser.add_argument(
        "--md-filepath",
        type=str,
        default="./repo/results/test.md",
        help="結果レポートの出力先パスを指定します。"
    )
    parser.add_argument(
        "--md-title",
        type=str,
        default="Test",
        help="結果レポートのタイトルを指定します。"
    )
    parser.add_argument(
        "--pull",
        type=str,
        help="hubからpullする値を指定します．"
    )
    parser.add_argument(
        "--tools",
        type=str,
        nargs="*",
        default=[
            "command_predictor",
            "parameter_predictor",
            "user_context_predictor",
            "shell_tool",
            "human",
        ],
        help=(
            "使用するツールを指定します。ツールは複数指定可能です。\n"
            "以下から選択してください。\n"
            "command_predictor: AWSコマンドを推定するツール\n"
            "parameter_predictor: AWSコマンドのパラメータを推定するツール\n"
            "user_context_predictor: ユーザーコンテキストを推定するツール\n"
            "shell_tool: シェルでコマンド実行するツール\n"
            "human: 人間が対話するツール\n"
        )
    )
    return parser.parse_args()


def get_input():
    print(
        "Insert your text. Enter 'q' or press Ctrl-D (or Ctrl-Z on Windows) "
        "to end.")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "q":
            break
        contents.append(line)
    return "\n".join(contents)


def main(args):
    set_config()
    llm = ChatOpenAI(temperature=0, model_name=args.llm)

    aws_query_engine = get_query_engine(args.aws_index_dir, llm)
    user_query_engine = get_query_engine(args.user_index_dir, llm)

    # Lang Chainで用いるツール群を定義
    tools = [
        CustomTool.command_predictor(aws_query_engine) if "command_predictor"
            in args.tools else None,
        CustomTool.parameter_predictor(aws_query_engine) if "parameter_predictor"
            in args.tools else None,
        CustomTool.user_context_predictor(user_query_engine) if "user_context_predictor"
            in args.tools else None,
        ShellTool() if "shell_tool" in args.tools else None,
        load_tools(["human"], input_func=get_input)[0] if "human"
            in args.tools else None
    ]
    tools = list(filter(None, tools))

    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        output_key="output",
    )

    agent_executor_conf = AgentExecutorConfig(
        llm=llm,
        tools=tools,
        memory=memory,
        agent_type=args.agent_type,
        pull=args.pull
    )

    agent_executor = AgentExecutorGen(agent_executor_conf).generate()

    conversation_log, e_sentences = AgentRunner(
        agent_executor=agent_executor,
        is_intaractive=args.interactive,
        qa_yaml=args.qa,
    ).run()

    experiment = Experiment(
        md_filepath=args.md_filepath,
        md_title=args.md_title,
        tool_names=", ".join([tool.name for tool in tools]),
        llm=args.llm,
        user_index_dir=args.user_index_dir,
        aws_index_dir=args.aws_index_dir,
        agent_type=args.agent_type,
    )

    gen_md(
        conversation_logs=conversation_log,
        experiment=experiment,
    )

    e_sentences.to_yaml(
        yaml_filepath="eval_sentence/test_ai_answer.yaml"
    )


if __name__ == "__main__":
    args = get_args()
    main(args)
