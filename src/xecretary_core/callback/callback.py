from time import time
from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain.callbacks.base import BaseCallbackHandler
from mdutils.mdutils import MdUtils
from tiktoken import encoding_for_model

from xecretary_core.conv_log.conv_log import ConversationLog
from xecretary_core.evaluation.evaluation_sentences import EvaluateSentence


class CustomCallbackHandler(BaseCallbackHandler):
    def __init__(self, md_file: MdUtils):
        super().__init__()
        self.user_input: Optional[str] = None
        self.chain_start_time: float = 0
        self.md_file: MdUtils = md_file
        self.e_sentence_list: List[EvaluateSentence] = list()

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        user_input = inputs.get("input")

        self.user_input = user_input
        self.chain_start_time = time()
        return

    def on_text(self, text: str, **kwargs: Any) -> None:
        encoding = encoding_for_model("gpt-4")
        token_count = len(encoding.encode(text))
        if token_count > 5000:
            print(f"token count is {token_count}")
        return

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        output = outputs.get("output", None)

        if output is None:
            # I don't know the reason to skip logging, but it may be necessary.
            return

        elapsed_time = time() - self.chain_start_time

        conversation_log = ConversationLog(
            input=self.user_input,
            output=output,
            intermediate_steps=outputs.get("intermediate_steps", None),
            chat_history=outputs.get("chat_history", None),
            elapsed_time=elapsed_time,
        )
        conversation_log.dump(self.md_file)

        self.e_sentence_list.append(
            EvaluateSentence(
                input=self.user_input,
                output=output,
                human_answer=None,
                evaluation=None,
            )
        )
        return
