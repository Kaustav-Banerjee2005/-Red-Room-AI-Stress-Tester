from fastapi import FastAPI
from pydantic import BaseModel

from models.gemini import ask_gemini

from classifier import safety_classifier
from policy import apply_policy
from logger import create_database, log_event

app = FastAPI()

# Create database on startup
create_database()


class ChatRequest(BaseModel):
    model: str
    message: str


@app.get("/")
def home():
    return {
        "status": "AI Sandbox Running"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    model_name = request.model.lower()
    user_input = request.message

    # -----------------------------
    # MODEL ROUTING
    # -----------------------------

    if model_name == "gemini":

        llm_output = ask_gemini(user_input)

    else:

        return {
            "error": f"Unsupported model: {model_name}"
        }

    # -----------------------------
    # PERSON 2 CLASSIFIER
    # -----------------------------

    risk = safety_classifier(
        user_input + "\n" + llm_output
    )

    # -----------------------------
    # PERSON 3 POLICY ENGINE
    # -----------------------------

    result = apply_policy(
        model_name,
        user_input,
        llm_output,
        risk
    )

    # -----------------------------
    # PERSON 3 LOGGER
    # -----------------------------

    log_event(
        model_name,
        user_input,
        llm_output,
        risk,
        result["action"]
    )

    return result