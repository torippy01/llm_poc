import argparse
import os
import time
from pathlib import Path

import openai
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage
from langchain.tools import ShellTool, tool
from llama_index import (LLMPredictor, ServiceContext, StorageContext,
                         load_index_from_storage)
from streamlit_chat import message


def set_config():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", type=str, default="gpt-4", help="推論用LLM名を指定します。")
    parser.add_argument(
        "--index-dir",
        type=str,
        default="test_index",
        help="インデックスのJsonファイルのディレクトリ名を指定します。",
    )
    return parser.parse_args()


set_config()

args = get_args()
llm = ChatOpenAI(temperature=0, model_name=args.llm)

storage_dir = Path("./storage") / args.index_dir
storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
index = load_index_from_storage(storage_context, index_id=args.index_dir)
llm_predictor = LLMPredictor(llm=llm)
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
query_engine = index.as_query_engine(service_context=service_context)


# プロンプトから該当するAWSコマンドを推定するツール
@tool
def command_predictor(query: str):
    """
    AWS CLIコマンドを取得するツール
    """
    response = query_engine.query(query)
    return response.response


# プロンプトからAWSコマンドの引数を推定するツール
@tool
def parameter_predictor_from_query(query: str):
    """
    AWS CLIコマンドの引数を取得するツール
    """
    response = query_engine.query(query)
    return response.response


def main():
    st.title("AWS秘書プロトタイピング - context less")
    st.caption("by Miura")

    # Lang Chainで用いるツール群を定義
    shell_tool = ShellTool()
    tools = [command_predictor, parameter_predictor_from_query, shell_tool]

    # 対話のmemoryをセッションステートから取得
    # 初回のみConversationBufferMemoryクラスから対話のmemoryを生成
    try:
        memory = st.session_state["memory"]
    except:
        memory = ConversationBufferMemory(return_messages=True)

    # zero-shot-react-descriptionについては下記URL参照
    # https://python.langchain.com/docs/modules/agents/agent_types/#zero-shot-react
    agent = initialize_agent(
        tools, llm, agent="zero-shot-react-description", memory=memory, verbose=True
    )

    if agent:
        st.session_state["agent"] = agent
        memory.chat_memory.add_ai_message("読込完了")

    user_message = st.text_input("質問")
    send_button = st.button("送信")

    # チャット履歴（HumanMessageやAIMessageなど）を格納する配列の初期化
    history = list()

    if send_button:
        agent = st.session_state["agent"]

        start = time.time()
        response = agent.run(user_message)
        elapsed_time = time.time() - start
        print(elapsed_time)

        memory.chat_memory.add_user_message(user_message)
        memory.chat_memory.add_ai_message(response)
        st.session_state["memory"] = memory

        try:
            history = memory.load_memory_variables({})["history"]
        except Exception as e:
            st.error(e)

    for index, chat_message in enumerate(reversed(history)):
        if isinstance(chat_message, HumanMessage):
            message(chat_message.content, is_user=True, key=2 * index)
        elif isinstance(chat_message, AIMessage):
            message(chat_message.content, is_user=False, key=2 * index + 1)


if __name__ == "__main__":
    main()
