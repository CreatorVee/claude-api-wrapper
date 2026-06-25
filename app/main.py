import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic

app = FastAPI(title="Claude API Wrapper")

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(request: AskRequest):
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": request.question}
            ],
        )
        answer = message.content[0].text
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
