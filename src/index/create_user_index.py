import logging

from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader

from index.utils import get_CL_args_for_context_index



def test() -> None:
    args = get_CL_args_for_context_index()
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
    return

