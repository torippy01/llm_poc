import argparse
import logging
import os

import openai
from dotenv import load_dotenv
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader


def set_config():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--index-id",
        type=str,
        default="user_context_index",
        help="インデックスIDを指定します。",
    )

    parser.add_argument(
        "--context-dir",
        type=str,
        default="./user_context",
        help="コンテキストのファイルが保存されるディレクトリを指定します。",
    )

    return parser.parse_args()


def main():
    set_config()
    args = get_args()
    logging.basicConfig(level=logging.INFO)

    logging.info("%sから を使ってドキュメントを取得しています．", args.context_dir)
    documents = SimpleDirectoryReader(input_dir=args.context_dir).load_data()
    logging.info("ドキュメントを取得しました．")

    logging.info("ドキュメントからGPTVectorStoreIndexを使ってインデックスを取得しています．")
    index = GPTVectorStoreIndex.from_documents(documents)

    index.set_index_id(args.index_id)
    logging.info("インデックスIDを%sに指定しました．", args.index_id)

    persist_dir = f"storage/{args.index_id}"
    index.storage_context.persist(persist_dir)
    logging.info("インデックスを%sに保存しました．", persist_dir)


if __name__ == "__main__":
    main()
