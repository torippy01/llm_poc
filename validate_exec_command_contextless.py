import argparse
import os
import time

import openai
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage
from langchain.tools import tool, ShellTool
from llama_index import (
    GPTVectorStoreIndex,
    ServiceContext,
    SimpleWebPageReader,
    StorageContext,
    LLMPredictor,
    load_index_from_storage,
)
from streamlit_chat import message
from pathlib import Path


def set_config():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--storage-id",
        type=str,
        default="doc_num",
        help="storage配下のディレクトリ名を指定します。"
    )
    return parser.parse_args()


def get_urls(path):
    with open(path, "r") as f:
        urls = [s.rstrip() for s in f.readlines()]
    return urls


def get_document(urls):
    return SimpleWebPageReader(html_to_text=True).load_data(urls)


def get_index(documents):
    return GPTVectorStoreIndex.from_documents(documents)


def load_index(storage_context):
    return load_index_from_storage(
        storage_context,
        index_id=VALIDATION_ID,
    )


set_config()

VALIDATION_ID = "doc_num"
PREDECTOR_MODEL = "gpt-3.5-turbo"
#PREDECTOR_MODEL = "gpt-4"
print(PREDECTOR_MODEL)
llm = ChatOpenAI(temperature=0, model=PREDECTOR_MODEL)

args = get_args()

storage_dir = Path("./storage") / args.storage_id

# storage contextが無ければ作成し、indexをロード
if storage_dir.exists():
    storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
    index = load_index(storage_context)
else:
    raise RuntimeError(f"{storage_dir}が存在しません。")

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
