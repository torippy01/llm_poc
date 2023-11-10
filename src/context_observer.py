"""
Usage :
python src/context_observer.py
"""

import os
import uvicorn

from context_fetcher.github_wiki import GithubWiki
from utils.utility import host_validation, port_validation

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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


if __name__ == "__main__":
    # CONTENT_OBSERVER_SV_HOSTから値が取れない場合は`localhost`
    _host = os.environ.get("CONTEXT_OBSERVER_SV_HOST")
    host = _host if host_validation(_host) else "localhost"

    # CONTENT_OBSERVER_SV_PORTから値が取れない場合は`3010`
    _port = os.environ.get("CONTEXT_OBSERVER_SV_PORT")
    port = int(_port) if port_validation(_port) else 3010  # type: ignore
    uvicorn.run("context_observer:app", port=port, reload=True, host=host)  # type: ignore
