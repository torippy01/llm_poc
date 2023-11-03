"""
Usage :
python src/validate_api.py -tm conf/beta.toml
python3 src/validate_api.py -tm conf/beta.toml
"""

import os
import uvicorn

from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel  # noqa: E402


load_dotenv()
app = FastAPI()


class Request(BaseModel):
    jobId: int
    text: str


@app.post("/github-wiki")
async def github_wiki(request: Request):
    print(request)
    return request


if __name__ == "__main__":
    host = os.environ.get("CONTENT_OBSERVER_SV_HOST")
    port = int(os.environ.get("CONTENT_OBSERVER_SV_PORT"))
    uvicorn.run("content_observer:app", port=port, reload=True, host=host)
