from pathlib import Path

from llama_index import (LLMPredictor, ServiceContext, StorageContext,
                         load_index_from_storage)


def get_query_engine(index_dir, llm):
    storage_dir = Path("./storage") / index_dir
    storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
    index = load_index_from_storage(storage_context, index_id=index_dir)
    llm_predictor = LLMPredictor(llm=llm)
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    return index.as_query_engine(service_context=service_context)
