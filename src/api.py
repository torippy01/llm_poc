import sys
sys.path.append("./src/")

import uvicorn
from agents.agent import AgentRunner
from config.config import Config
from fastapi import FastAPI, HTTPException
from typing import Union, Dict
from utils.utility import set_up

set_up()
conf = Config.fetch_config()
agent_runner = AgentRunner(conf)
app = FastAPI()


def query(text: str) -> Union[None, str]:
    answer = agent_runner.run_agent_with_single_action(
        user_message=text
    )
    return answer


@app.get("/")
def bot(
    job_id: int,
    text: Union[str, None] = None
) -> Dict[str, Union[int, str]]:

    if text is None:
        raise HTTPException(
            status_code=400,
            detail="質問文が見当たりませんでした"
        )

    answer = query(text)
    if not answer:
        raise HTTPException(
            status_code=500,
            detail="エージェントが回答できませんでした"
        )

    return {"job_id": job_id, "answer": answer}


if __name__ == "__main__":
    uvicorn.run("api:app", port=3999, reload=True)
