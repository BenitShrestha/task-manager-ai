from datetime import datetime

from pydantic import BaseModel

from app.models.task import TaskPriority


class GenerateRequest(BaseModel):
    text: str

    class Config:
        str_max_length = 2000


class GeneratedTask(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.medium
    deadline: datetime | None = None


class GeneratedTaskList(BaseModel):
    tasks: list[GeneratedTask]