from time import time
from typing import Dict, Any, Optional, List

from langchain.callbacks.base import BaseCallbackHandler

from mdutils.mdutils import MdUtils

from tiktoken import encoding_for_model

from uuid import UUID

from conv_log.conv_log import ConversationLog




class CustomCallbackHandler(BaseCallbackHandler):
    md: MdUtils
    conversation_logs: List[ConversationLog] = list()
    user_input: str
    chain_start_time: float


    def __init__(
        self,
        md: MdUtils
    ):
        super().__init__()
        self.md = md


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
        """Run when chain starts running."""
        user_input = inputs.get("input")
        if user_input is None:
            raise RuntimeError(
                "ユーザーは必ず入力文を入れているはずなのにありません！これはいくないです！"
            )

        self.user_input = user_input
        self.chain_start_time = time()
        return


    def on_text(self, text: str, **kwargs: Any) -> None:
        """Run on arbitrary text."""
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
            raise RuntimeError(
                "チェインが終わったというのに最終回答がありません！これはいくないです！"
            )

        elapsed_time = time() - self.chain_start_time
        conversation_log = ConversationLog(
            input=self.user_input,
            output=output,
            intermediate_steps=outputs.get("intermediate_steps", None),
            chat_history=outputs.get("chat_history", None),
            elapsed_time=elapsed_time,
        )
        conversation_log.dump(self.md)
        return
