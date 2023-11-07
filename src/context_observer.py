"""
Usage :
python src/validate_api.py -tm conf/beta.toml
python3 src/validate_api.py -tm conf/beta.toml
"""

import os
import uvicorn

from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from context_fetcher.github_wiki import GithubWiki


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
            status_code=500,
            detail="Unexpected error is occured on github page update."
        )
    wiki = GithubWiki(url=request.url)
    wiki.create_index()
    return request


# Use for AWS Target Group health check
@app.get("/health")
async def health():
    return


if __name__ == "__main__":
    host = os.environ.get("CONTENT_OBSERVER_SV_HOST")
    port = int(os.environ.get("CONTENT_OBSERVER_SV_PORT"))
    uvicorn.run("content_observer:app", port=port, reload=True, host=host)
