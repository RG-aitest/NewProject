from fastapi import FastAPI
from pydantic import BaseModel
from AIBot import run_agent  # your agentic ReAct logic
import uvicorn

app = FastAPI(title="Agentic Water Quality Chatbot API")


# -----------------------------
# Pydantic models for /ask
# -----------------------------
class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str


# -----------------------------
# Health check endpoint
# -----------------------------
@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Backend is running"}


# -----------------------------
# Main chatbot endpoint
# -----------------------------
@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Receives a question in JSON, passes it to the agent, and returns the answer.
    Example request:
        {
            "query": "What is the water quality of the Mississippi River?"
        }
    """
    question = request.query.strip()
    if not question:
        return QueryResponse(answer="No question provided.")

    # Call your LangChain / Ollama agent logic
    answer = run_agent(question)
    return QueryResponse(answer=answer)


# -----------------------------
# Local execution entry point
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
