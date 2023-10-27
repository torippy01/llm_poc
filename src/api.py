from typing import Union, Dict

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def bot(job_id: int, text: Union[str, None] = None) -> Dict[str, Union[int, str]]:
    answer = ""
    return {"job_id": job_id, "answer": answer}