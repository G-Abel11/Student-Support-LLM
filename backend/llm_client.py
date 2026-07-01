# backend/llm_client.py

import httpx
from config import OLLAMA_BASE_URL, MODEL_NAME, SYSTEM_PROMPT

async def ask_llm(question: str) -> str:
    """
    Sends a question to the Ollama API and returns the model's response.
    """

    # Inject the actual question into the prompt template
    full_prompt = SYSTEM_PROMPT.format(question=question)

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return data["response"]