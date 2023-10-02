"""
python src/validate.py \
    --aws-index-dir aws_ref \
    --qa repo/qa/qa1.yaml
"""

import argparse
import os
import time
import yaml

import openai

from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import ShellTool
from llama_index import (
    ServiceContext,
    StorageContext,
    LLMPredictor,
    load_index_from_storage,
)
from pathlib import Path

from utils.generate_markdown import gen_md
from utils.schema import Experiment
from utils.tools import CustomTool


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
        default="test_index",
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
        help="エージェントのタイプを指定します。"
    )
    parser.add_argument(
        "--qa",
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
    return parser.parse_args()


def get_query_engine(index_dir, llm):
    storage_dir = Path("./storage") / index_dir
    storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
    index = load_index_from_storage(storage_context, index_id=index_dir)
    llm_predictor = LLMPredictor(llm=llm)
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    return index.as_query_engine(service_context=service_context)


def main():
    set_config()
    args = get_args()
    llm = ChatOpenAI(temperature=0, model_name=args.llm)

    aws_query_engine = get_query_engine(args.aws_index_dir, llm)
    user_query_engine = get_query_engine(args.user_index_dir, llm)

    # Lang Chainで用いるツール群を定義
    shell_tool = ShellTool()

    tools = [
        CustomTool.command_predictor(aws_query_engine),
        CustomTool.parameter_predictor_from_query(aws_query_engine),
        CustomTool.user_context_predictor(user_query_engine),
        shell_tool
    ]

    # zero-shot-react-descriptionについては下記URL参照
    # https://python.langchain.com/docs/modules/agents/agent_types/#zero-shot-react
    agent = initialize_agent(
        tools,
        llm,
        agent=args.agent_type,
        verbose=True,
        return_intermediate_steps=True,
    )

    # QAのyamlファイルをオープン
    with open(args.qa) as f:
        qas = yaml.safe_load(f)

    results = list()
    ai_answers = list()

    # 質問群に対してエージェントが回答
    # 回答結果をQAに追加
    for qa in qas:
        question = qa["question"]
        start = time.time()
        response = agent.invoke(input={"input": question})
        elapsed_time = time.time() - start
        results.append({"response": response, "elapsed_time": elapsed_time})
        ai_answers.append({
            "question": question,
            "final_answer": response["output"],
            "answer": qa["answer"],
            "evaluation": None,
        })

    experiment = Experiment(
        args.md_filepath,
        args.md_title,
        [tool.name for tool in tools],
        args.llm,
        args.user_index_dir,
        args.aws_index_dir,
        args.agent_type
    )

    gen_md(
        results,
        experiment=experiment,
    )

    yaml_filepath = "repo/ai_answer/test_ai_answer.yaml"

    with open(yaml_filepath, "w") as f:
        yaml.dump(ai_answers, f, allow_unicode=True)


if __name__ == "__main__":
    main()
