import os

import openai
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage
from langchain.tools import tool
from llama_index import (
    GPTVectorStoreIndex,
    ServiceContext,
    SimpleDirectoryReader,
    StorageContext,
    LLMPredictor,
    load_index_from_storage,
)
from streamlit_chat import message
from pathlib import Path


def set_config():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


def get_document():
    document_path = Path("./doc/single_doc")
    if not document_path.exists():
        raise RuntimeError("ドキュメントのパスが見つかりません。")
    return SimpleDirectoryReader(input_dir="./doc/single_doc").load_data()


def get_index(documents):
    return GPTVectorStoreIndex.from_documents(documents)


def create_storage_context(validation_id):
    documents = get_document()
    index = get_index(documents)
    index.set_index_id(validation_id)
    index.storage_context.persist(f"storage/{validation_id}")
    return StorageContext.from_defaults(persist_dir=f"storage/{validation_id}")


def load_index(storage_context, validation_id):
    return load_index_from_storage(
        storage_context,
        index_id=validation_id,
    )


set_config()

VALIDATION_ID = "single_doc"
llm = ChatOpenAI(temperature=0)  # デフォルトで"gpt-3.5-turbo"を使用

storage_dir = Path("./storage") / VALIDATION_ID

# storage contextが無ければ作成し、indexをロード
if storage_dir.exists():
    storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
    index = load_index(storage_context, VALIDATION_ID)
else:
    storage_context = create_storage_context(VALIDATION_ID)
    index = load_index(storage_context, VALIDATION_ID)

llm_predictor = LLMPredictor(llm=llm)
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

query_engine = index.as_query_engine(service_context=service_context)


# プロンプトから該当するAWSコマンドを推定するツール
@tool
def command_predictor(query: str):
    """
    ユーザーの要望を満たすAWSコマンドを表示します。
    """
    response = query_engine.query(query)
    return response.response


# プロンプトからAWSコマンドの引数を推定するツール
@tool
def parameter_predictor_from_query(query: str):
    """
    ユーザーの質問文中から、AWSコマンドに必要な引数を抽出して表示してください。
    もし引数が見つからない場合は、ユーザーに引数が見当たらない旨を伝えてください。
    """
    response = query_engine.query(query)
    return response.response


def main():
    st.title("AWS秘書プロトタイピング - single document")
    st.caption("by Miura")

    # Lang Chainで用いるツール群を定義
    tools = [command_predictor, parameter_predictor_from_query]

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
        response = agent.run(user_message)

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
