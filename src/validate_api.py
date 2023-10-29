import argparse
import sys
from typing import Dict, Optional, Union  # noqa: E402

from fastapi import FastAPI, HTTPException  # noqa: E402
import uvicorn

from agents.agent import AgentRunner  # noqa: E402
from agents.conf import Config
from utils.utility import set_up  # noqa: E402


"""
Usage :
python src/validate_api.py -tm conf/_test.toml
python3 src/validate_api.py -tm conf/_test.toml
"""


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--conf-toml",
        "-tm",
        type=str,
        help="Please specify config TOML file."
    )
    return parser.parse_args()


sys.path.append("./src/")
app = FastAPI()

set_up()
conf = Config.fetch(get_args())
agent_runner = AgentRunner(conf)


def query(text: str) -> Optional[str]:
    return agent_runner.run_agent_with_single_action(user_message=text)


@app.get("/")
def bot(
    job_id: int,
    text: Optional[str] = None
) -> Dict[str, Union[int, str]]:

    if text is None:
        raise HTTPException(status_code=400, detail="質問文が見当たりませんでした")

    answer = query(text)
    if not answer:
        raise HTTPException(status_code=500, detail="エージェントが回答できませんでした")

    return {"job_id": job_id, "answer": answer}


if __name__ == "__main__":
    uvicorn.run("api:app", port=3999, reload=True)
