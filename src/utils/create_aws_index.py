"""
# urlからAWSインデックスを作成する場合
python src/create_aws_index.py \
    --start 0 \
    --end 600 \
    --index-id aws_url \
    --urls-path ./aws_context/urls/

# ドキュメントからAWSインデックスを作成する場合
python src/create_aws_index.py \
    --start 0 \
    --end 1 \
    --index-id aws_ref \
    --docs-path ./aws_context/ref_doc
"""

import argparse
import os
from glob import glob
from typing import List

import openai
from dotenv import load_dotenv
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, SimpleWebPageReader


def set_config():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


def get_args():
    parser = argparse.ArgumentParser()

    # Document Resource
    parser.add_argument(
        "--urls-path",
        type=str,
        help="URLの記載されるファイルのパスを指定します。",
    )

    parser.add_argument(
        "--docs-path",
        type=str,
        help="",
    )

    # URL configuration
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="インデックス化するドキュメントリソースの最初の位置を指定します。",
    )

    parser.add_argument(
        "--end",
        type=int,
        default=10,
        help="インデックス化するドキュメントリソースの最後の位置を指定します。",
    )

    # General configuration
    parser.add_argument(
        "--index-id",
        type=str,
        help="インデックスIDを指定します。",
    )

    return parser.parse_args()


def get_urls(path: str, start: int = 0, end: int = 100) -> List[str]:
    with open(path, "r") as f:
        urls = [s.rstrip() for s in f.readlines()]
    return urls[start:end]


def get_document(path: str, start: int = 0, end: int = 100):
    return glob(f"{path}/*")[start:end]


class Document:
    def __init__(self, urls_path, docs_path, start, end) -> None:
        self.urls_path: str = urls_path
        self.docs_path: str = docs_path
        self.start: int = start
        self.end: int = end
        self.validate: str = self.get_validate()
        self.document_resource: List[str] = self.get_document_resource()

    def get_validate(self) -> str:
        # documentを優先
        if self.docs_path:
            return "doc"
        elif self.urls_path:
            return "url"
        else:
            raise ValueError("ドキュメントリソースのパスが指定されていません")

    def get_document_resource(self) -> List[str]:
        if self.validate == "url":
            return get_urls(self.urls_path, self.start, self.end)
        elif self.validate == "doc":
            return get_document(self.docs_path, self.start, self.end)
        else:
            raise RuntimeError("Unexpected Error!!!")

    def load_data(self):
        if self.validate == "url":
            return SimpleWebPageReader(html_to_text=True).load_data(
                self.document_resource
            )
        elif self.validate == "doc":
            return SimpleDirectoryReader(input_files=self.document_resource).load_data()


def main():
    set_config()
    args = get_args()

    docs = Document(args.urls_path, args.docs_path, args.start, args.end).load_data()

    print("documentの読み込み完了")
    index = GPTVectorStoreIndex.from_documents(docs)

    index.set_index_id(args.index_id)
    print(f"インデックスIDを{args.index_id}に指定しました．")

    persist_dir = f"storage/{args.index_id}"
    index.storage_context.persist(persist_dir)
    print(f"インデックスを{persist_dir}に保存しました．")


if __name__ == "__main__":
    main()
