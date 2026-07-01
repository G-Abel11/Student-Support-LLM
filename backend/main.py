# backend/main.py

import logging
import os
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import APP_HOST, APP_PORT, LOG_FILE
from llm_client import ask_llm

# ── Logging setup ──────────────────────────────────────────────
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── FastAPI app ────────────────────────────────────────────────
app = FastAPI(
    title="University Student Support Assistant",
    description="A self-hosted LLM backend for student queries",
    version="1.0.0"
)

# ── CORS middleware ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request model ──────────────────────────────────────────────
class QuestionRequest(BaseModel):
    question: str

# ── Startup/shutdown events ────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 55)
    logger.info("  University Student Support Assistant started")
    logger.info(f"  Model    : llama3.2:1b")
    logger.info(f"  Log file : {LOG_FILE}")
    logger.info("=" * 55)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=" * 55)
    logger.info("  Application shutting down")
    logger.info("=" * 55)

# ── Endpoints ──────────────────────────────────────────────────
@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {"message": "University Student Support Assistant is running."}


@app.get("/health")
def health_check():
    logger.info("Health check called")
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "model": "llama3.2:1b"
    }


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    question = request.question.strip()

    # ── Empty question ─────────────────────────────────────────
    if not question:
        logger.warning("REJECTED  | Empty question received")
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # ── Log incoming question ──────────────────────────────────
    logger.info(f"QUESTION  | {question}")

    try:
        answer = await ask_llm(question)

        # ── Log the answer ─────────────────────────────────────
        logger.info(f"ANSWER    | {answer[:120]}{'...' if len(answer) > 120 else ''}")
        logger.info(f"LENGTH    | {len(answer)} characters")

        return {
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }

    except httpx.ConnectError:
        logger.error("ERROR     | Could not connect to Ollama — is it running?")
        raise HTTPException(
            status_code=503,
            detail="LLM service is unavailable. Please ensure Ollama is running."
        )
    except httpx.TimeoutException:
        logger.error("ERROR     | Request to Ollama timed out")
        raise HTTPException(
            status_code=504,
            detail="The model took too long to respond. Please try again."
        )
    except Exception as e:
        logger.error(f"ERROR     | Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ── Run directly ───────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)