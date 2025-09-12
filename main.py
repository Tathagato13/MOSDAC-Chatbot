from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from typing import Dict

from chatbot_logic.retriever import get_response, ConversationManager
from chatbot_logic.query_engine import load_vector_store

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

conversation_manager = ConversationManager()
index, chunks = load_vector_store()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_model=Dict)
async def chat(message: str = Form(...), session_id: str = Form(None)):
    if not session_id:
        session_id = str(uuid4())

    response = get_response(message, session_id)
    if not response or response.strip().lower() in ["", "undefined"]:
        response = "❌ Sorry, I couldn’t generate a response. Try rephrasing."

    return {"response": response, "session_id": session_id}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
