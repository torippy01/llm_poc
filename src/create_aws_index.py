import argparse
import logging
import os
import openai

from dotenv import load_dotenv
from llama_index import (
    GPTVectorStoreIndex,
    SimpleWebPageReader,
)


def set_config():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--start-url",
        type=int,
        default=0,
        help="インデックス化する最初のURLの位置を指定します。",
    )

    parser.add_argument(
        "--end-url",
        type=int,
        default=10,
        help="インデックス化する最後のURLの位置を指定します。",
    )

    parser.add_argument(
        "--index-id",
        type=str,
        default="test_index",
        help="インデックスIDを指定します。",
    )

    parser.add_argument(
        "--urls-path",
        type=str,
        default="./aws_context/urls.txt",
        help="URLの記載されるファイルのパスを指定します。",
    )

    return parser.parse_args()

def get_urls(path):
    with open(path, "r") as f:
        urls = [s.rstrip() for s in f.readlines()]
    return urls


def main():
    set_config()
    args = get_args()
    logging.basicConfig(level=logging.INFO)

    urls = get_urls(args.urls_path)[args.start_url:args.end_url]
    logging.info("URLsを取得しました．")

    logging.info("URLからSimpleWebPageReaderを使ってドキュメントを取得しています．")
    documents = SimpleWebPageReader(html_to_text=True).load_data(urls)
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
