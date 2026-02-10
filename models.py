from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

class TaskContext(BaseModel):
    id: int
    title: str
    completed: bool
    priority: Optional[str] = None
    description: Optional[str] = None
    dueDate: Optional[str] |None

class PlanItem(BaseModel):
    taskId: Optional[int]
    title: Optional[str]
    meta: Optional[str] = None


class AiResponse(BaseModel):
    type: Optional[str] = "plan"
    title: Optional[str] = None
    items: Optional[List[PlanItem]] = None
    followUps: Optional[List[str]] = None

class AIContextItem(BaseModel):
    prompt: str
    previousAIresponse: AiResponse
    created_at: Optional[datetime] = None


class AiAskRequest(BaseModel):
    prompt: str
    context: List[AIContextItem] = []
    tasks: List[TaskContext]
