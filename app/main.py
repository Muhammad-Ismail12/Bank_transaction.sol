from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .agent import AppointmentAgent
from .memory import store


app = FastAPI(title="Doctor Appointment AI Agent")
agent = AppointmentAgent()


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant|tool)$")
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    content: str
    tool_calls: List[Dict[str, Any]]


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    try:
        result = agent.run([m.model_dump() for m in req.messages])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(**result)


@app.get("/api/doctors")
async def api_doctors(specialty: Optional[str] = None, location: Optional[str] = None) -> Dict[str, Any]:
    return {"doctors": store.list_doctors(specialty, location)}


@app.get("/api/appointments")
async def api_appointments() -> Dict[str, Any]:
    return {"appointments": store.list_appointments()}