"""
Usage :
python src/context_observer.py
"""

import os
import re
import uvicorn

from context_fetcher.github_wiki import GithubWiki

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

load_dotenv()
app = FastAPI()


class Request(BaseModel):
    action: str
    repo: str
    url: str


@app.post("/github-wiki")
async def github_wiki(request: Request):
    if request.action not in ["created", "edited", "deleted"]:
        raise HTTPException(
            status_code=500, detail="Unexpected error is occured on github page update."
        )
    wiki = GithubWiki(url=request.url)
    wiki.create_index()
    return request


# Use for AWS Target Group health check
@app.get("/health")
async def health():
    return


def host_validation(host: Optional[str]):
    # hostが文字列であればTrue
    # TODO: 文字列の内容を加味すべき
    if not host:
        return False
    elif isinstance(host, str):
        return True


def port_validation(port: Optional[str]):
    # portが半角数字文字列であればTrue
    # それ以外はFalse
    if not port:
        return False
    return True if re.fullmatch("[0-9]+", port) else False


if __name__ == "__main__":
    # CONTENT_OBSERVER_SV_HOSTから値が取れない場合は`localhost`
    _host = os.environ.get("CONTENT_OBSERVER_SV_HOST")
    host = _host if host_validation(_host) else "localhost"

    # CONTENT_OBSERVER_SV_PORTから値が取れない場合は`3010`
    _port = os.environ.get("CONTENT_OBSERVER_SV_PORT")
    port = int(_port) if port_validation(_port) else 3010  # type: ignore
    uvicorn.run("content_observer:app", port=port, reload=True, host=host)  # type: ignore
