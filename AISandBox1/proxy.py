from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

from models.gemini import ask_gemini
from classifier import safety_classifier
from policy import apply_policy
from logger import create_database, log_event

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

create_database()

class ChatRequest(BaseModel):
    model: str
    message: str

@app.get("/")
def home():
    return {"status": "AI Sandbox Running"}

@app.post("/chat")
def chat(request: ChatRequest):
    model_name = request.model.lower()
    user_input = request.message

    if model_name == "gemini":
        llm_output = ask_gemini(user_input)
    else:
        llm_output = f"{model_name.upper()} — not connected yet."

    risk = safety_classifier(user_input + "\n" + llm_output)
    result = apply_policy(model_name, user_input, llm_output, risk)
    log_event(model_name, user_input, llm_output, risk, result["action"])
    return result

@app.get("/logs")
def get_logs():
    conn = sqlite3.connect("logs.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]