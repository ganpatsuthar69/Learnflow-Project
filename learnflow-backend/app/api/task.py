from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import date
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import Student
from app.models.task import Task
from app.schema.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_task = Task(
        student_id=current_user.id,
        **task.dict(),
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    task_date: Optional[date] = Query(None, alias="date", description="Filter by planned date"),
    task_status: Optional[str] = Query(None, alias="status", description="Filter by status"),
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).filter(Task.student_id == current_user.id)

    if task_date:
        query = query.filter(Task.planned_date == task_date)

    if task_status:
        query = query.filter(Task.status == task_status)

    query = query.order_by(Task.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).filter(Task.id == task_id, Task.student_id == current_user.id)
    )
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.get("/summary")
async def get_task_summary(
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()

    # Auto-update missed tasks
    result = await db.execute(
        select(Task).filter(
            Task.student_id == current_user.id,
            Task.status == "pending",
            Task.planned_date < today,
        )
    )
    missed_tasks = result.scalars().all()

    for task in missed_tasks:
        task.status = "missed"

    if missed_tasks:
        await db.commit()

    # Get counts using func.count for efficiency
    total_result = await db.execute(
        select(func.count()).select_from(Task).filter(Task.student_id == current_user.id)
    )
    total = total_result.scalar()

    completed_result = await db.execute(
        select(func.count()).select_from(Task).filter(
            Task.student_id == current_user.id, Task.status == "completed"
        )
    )
    completed = completed_result.scalar()

    pending_result = await db.execute(
        select(func.count()).select_from(Task).filter(
            Task.student_id == current_user.id, Task.status == "pending"
        )
    )
    pending = pending_result.scalar()

    missed_result = await db.execute(
        select(func.count()).select_from(Task).filter(
            Task.student_id == current_user.id, Task.status == "missed"
        )
    )
    missed = missed_result.scalar()

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "missed": missed,
    }
