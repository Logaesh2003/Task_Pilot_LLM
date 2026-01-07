from pydantic import BaseModel
from typing import List, Optional

class TaskContext(BaseModel):
    id: int
    title: str
    completed: bool
    priority: Optional[str] = None
    description: Optional[str] = None
    dueDate: Optional[str] |None

class AiAskRequest(BaseModel):
    prompt: str
    context: str
    tasks: List[TaskContext]