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
    action: str
    title: str
    url: str


@app.post("/github-wiki")
async def github_wiki(request: Request):
    print(request)
    return request


# Use for AWS Target Group health check
@app.get("/health")
async def health():
    return


if __name__ == "__main__":
    host = os.environ.get("CONTENT_OBSERVER_SV_HOST")
    port = int(os.environ.get("CONTENT_OBSERVER_SV_PORT"))
    uvicorn.run("content_observer:app", port=port, reload=True, host=host)
