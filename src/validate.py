"""
python src/validate.py \
    --agent-type chat-zero-shot-react-description \
    --interactive
"""

import argparse
import os
import time
import yaml

import openai

from typing import Callable, Any, Tuple, List

from dotenv import load_dotenv

from langchain import hub
from langchain.agents import initialize_agent, load_tools, AgentExecutor
from langchain.agents.output_parsers.react_single_input import ReActSingleInputOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.chat_models import ChatOpenAI
from langchain.tools import ShellTool
from langchain.tools.render import render_text_description
from langchain.memory import ConversationBufferMemory

from utils.generate_markdown import gen_md
from utils.schema import (
    Experiment,
    ConversationLog,
    EvaluateSentence,
    EvaluateSentences
)
from utils.tools import CustomTool
from utils.query_engines import get_query_engine


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


def time_measurement(func: Callable, val: Any) -> Any:
    start = time.time()
    response = func(**val)
    elapsed_time = time.time() - start
    return response, elapsed_time


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


def run_agent_with_interactive(
        agent: AgentExecutor
) -> Tuple[List[ConversationLog], EvaluateSentences]:

    conversation_log = list()
    e_sentences = EvaluateSentences()

    while True:
        print(
            "AIへのメッセージを書いてください。\n"
            "終了する場合は'exit'と入力してください。"
        )

        user_message = input()
        if user_message == "exit":
            break

        response, elapsed_time = time_measurement(
            agent.invoke,
            {"input": {"input": user_message}}
        )

        conversation_log.append(
            ConversationLog(
                input=response.get("input"),
                output=response.get("output"),
                intermediate_steps=response.get("intermediate_steps", None),
                chat_history=response.get("chat_history", None),
                elapsed_time=elapsed_time
            )
        )

        e_sentences.append(
            EvaluateSentence(
                input=response.get("input"),
                output=response.get("output"),
                human_answer=None,
                evaluation=None
            )
        )
    return conversation_log, e_sentences


def run_agent_with_Q_and_A(
        agent: AgentExecutor
) -> Tuple[List[ConversationLog], EvaluateSentences]:

    conversation_log = list()
    e_sentences = EvaluateSentences()

    # QAのyamlファイルをオープン
    with open(args.qa) as f:
        qas = yaml.safe_load(f)

    # 質問群に対してエージェントが回答
    # 回答結果をQAに追加
    for qa in qas:
        user_message = qa["question"]
        response, elapsed_time = time_measurement(
            agent.invoke,
            {"input": {"input": user_message}}
        )

        conversation_log.append(
            ConversationLog(
                input=response.get("input"),
                output=response.get("output"),
                intermediate_steps=response.get("intermediate_steps", None),
                chat_history=response.get("chat_history", None),
                elapsed_time=elapsed_time
            )
        )

        e_sentences.append(
            EvaluateSentence(
                input=response.get("input"),
                output=response.get("output"),
                human_answer=qa["answer"],
                evaluation=None
            )
        )
    return conversation_log, e_sentences


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

    return_intermediate_steps = False if args.agent_type in [
        "conversational-react-description"
    ] else True


    if args.pull:
        prompt = hub.pull(args.pull)
        prompt = prompt.partial(
            tools=render_text_description(tools),
            tool_names=", ".join([t.name for t in tools]),
        )
        llm_with_stop = llm.bind(stop=["\nObservation"])
        agent = {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_str(x['intermediate_steps']),
            "chat_history": lambda x: x["chat_history"]
        } | prompt | llm_with_stop | ReActSingleInputOutputParser()
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            memory=memory
        )

    else:
        agent = args.agent_type
        agent_executor = initialize_agent(
            agent=agent,
            tools=tools,
            llm=llm,
            memory=memory,
            verbose=True,
            return_intermediate_steps=return_intermediate_steps,
        )

    # インタラクティブモード
    if args.interactive:
        (conversation_log, e_sentences) = run_agent_with_interactive(agent_executor)

    # 事前に準備したユーザーメッセージに対して回答
    else:
        (conversation_log, e_sentences) = run_agent_with_Q_and_A(agent_executor)

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
        yaml_filepath="repo/ai_answer/test_ai_answer.yaml"
    )


if __name__ == "__main__":
    args = get_args()
    main(args)
