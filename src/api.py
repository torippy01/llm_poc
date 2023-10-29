"""
python src/api.py --conf-toml conf/beta.toml
"""
import os
import sys

import requests
import uvicorn

sys.path.append("./src/")

from typing import Optional, TypedDict  # noqa: E402

from fastapi import FastAPI, HTTPException  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from agents.agent import AgentRunner  # noqa: E402
from config.config import Config  # noqa: E402
from utils.utility import set_up  # noqa: E402

set_up()
conf = Config.fetch_config()
agent_runner = AgentRunner(conf)
app = FastAPI()


class Request(BaseModel):
    jobId: int
    text: str


class Response(BaseModel):
    jobId: int
    text: str


class Body(TypedDict):
    jobId: int
    text: str


def query(user_message: str) -> Optional[str]:
    try:
        answer = agent_runner.run_agent_with_single_action(
            user_message=user_message
        )
        return answer
    except:
        return


def sender(body: Body) -> None:
    url = os.environ.get("SEND_MESSAGE_URL")
    requests.post(url, json=body)


@app.post("/")
async def bot(request: Request) -> Response:
    if request.text is None:
        raise HTTPException(status_code=400, detail="質問文が見当たりませんでした")

    answer = query(request.text)

    if not answer:
        fail_message = "エージェントが回答できませんでした"
        body: Body = {
            "jobId": request.jobId,
            "text": fail_message
        }
        sender(body)

        raise HTTPException(status_code=500, detail=fail_message)

    body: Body = {
        "jobId": request.jobId,
        "text": answer
    }

    sender(body)

    return Response(jobId=request.jobId, text=answer)


if __name__ == "__main__":
    host = os.environ.get("XECRETARY_SV_HOST")
    port = int(os.environ.get("XECRETARY_SV_PORT"))
    uvicorn.run("api:app", port=port, reload=True, host=host)
