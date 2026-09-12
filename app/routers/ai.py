from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user
from app.database import get_db
from app.limiter import limiter
from app.models.task import Task
from app.models.user import User
from app.schemas.ai import GenerateRequest
from app.schemas.task import TaskOut
from app.services.ai_service import AIGenerationError, generate_tasks_from_text

router = APIRouter(prefix="/tasks", tags=["ai"])


@router.post("/generate", response_model=list[TaskOut])
@limiter.limit("5/minute")
def generate_tasks(
    request: Request,
    payload: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.text.strip():
        raise HTTPException(status_code=422, detail="Text must not be empty")

    try:
        result = generate_tasks_from_text(payload.text)
    except AIGenerationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not result.tasks:
        return []

    tasks = [
        Task(**t.model_dump(), owner_id=current_user.id) for t in result.tasks
    ]
    db.add_all(tasks)
    db.commit()
    for t in tasks:
        db.refresh(t)
    return tasks