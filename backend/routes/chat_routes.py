"""
PAIMANA AI Assistant & Executive Memo Generator Routes
"""

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from backend.models.llm_assistant import paimana_assistant

router = APIRouter(prefix="/api/chat", tags=["AI Copilot & Executive Memos"])

class ChatQueryRequest(BaseModel):
    query: str

@router.post("/query")
def chat_query(req: ChatQueryRequest):
    """
    Submits natural language questions to PAIMANA AI Assistant.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return paimana_assistant.answer_query(req.query)

@router.get("/brief/{project_id}")
def generate_project_brief(project_id: str):
    """
    Generates a formal MoSPI Executive Escalation Brief for a specified project.
    """
    res = paimana_assistant.generate_executive_brief(project_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
