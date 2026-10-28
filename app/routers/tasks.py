"""Task endpoints nested under projects."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project, Task
from app.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


def require_project(project_id: int, db: Session) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int, payload: TaskCreate, db: Session = Depends(get_db)
) -> Task:
    require_project(project_id, db)
    task = Task(project_id=project_id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[TaskRead])
def list_tasks(
    project_id: int,
    offset: int = 0,
    limit: int = 50,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
) -> list[Task]:
    require_project(project_id, db)
    if offset < 0:
        raise HTTPException(status_code=422, detail="offset must be non-negative")
    if not 1 <= limit <= 100:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 100")
    query = select(Task).where(Task.project_id == project_id)
    if status_filter is not None:
        if status_filter not in {"todo", "in_progress", "done"}:
            raise HTTPException(status_code=422, detail="Invalid task status")
        query = query.where(Task.status == status_filter)
    return list(db.scalars(query.order_by(Task.id).offset(offset).limit(limit)))


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    project_id: int, task_id: int, db: Session = Depends(get_db)
) -> Task:
    require_project(project_id, db)
    task = db.scalar(
        select(Task).where(Task.id == task_id, Task.project_id == project_id)
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    project_id: int,
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
) -> Task:
    require_project(project_id, db)
    task = db.scalar(
        select(Task).where(Task.id == task_id, Task.project_id == project_id)
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    project_id: int, task_id: int, db: Session = Depends(get_db)
) -> Response:
    require_project(project_id, db)
    task = db.scalar(
        select(Task).where(Task.id == task_id, Task.project_id == project_id)
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
