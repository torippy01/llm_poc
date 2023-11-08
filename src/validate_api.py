"""
Usage :
python src/validate_api.py -tm conf/beta.toml
python3 src/validate_api.py -tm conf/beta.toml
"""

import argparse
import os
import requests
import sys

import uvicorn

sys.path.append("./src/")

from typing import Optional, TypedDict  # noqa: E402

from fastapi import FastAPI, HTTPException  # noqa: E402

from agents.agent import AgentRunner  # noqa: E402
from agents.conf import Config
from pydantic import BaseModel  # noqa: E402
from utils.utility import set_up, host_validation, port_validation  # noqa: E402


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conf-toml", "-tm", type=str, help="Please specify config TOML file."
    )
    return parser.parse_args()


set_up()
conf = Config.fetch(get_args().conf_toml)
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
    agent_runner = AgentRunner(conf)
    try:
        answer = agent_runner.run_agent_with_single_action(user_message=user_message)
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
        body: Body = {"jobId": request.jobId, "text": fail_message}
        sender(body)

        raise HTTPException(status_code=500, detail=fail_message)

    body: Body = {"jobId": request.jobId, "text": answer}

    sender(body)

    return Response(jobId=request.jobId, text=answer)


if __name__ == "__main__":
    # CONTENT_OBSERVER_SV_HOSTから値が取れない場合は`localhost`
    _host = os.environ.get("XECRETARY_SV_HOST")
    host = _host if host_validation(_host) else "localhost"

    # CONTENT_OBSERVER_SV_PORTから値が取れない場合は`3010`
    _port = os.environ.get("XECRETARY_SV_PORT")
    port = int(_port) if port_validation(_port) else 3999  # type: ignore
    uvicorn.run("validate_api:app", port=port, reload=True, host=host)  # type: ignore
