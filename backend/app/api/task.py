from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import Student
from app.models.task import Task
from app.schema.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_task = Task(
        student_id=current_user.id,
        **task.dict()
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    date: Optional[date] = Query(None, description="Filter by planned date"),
    status: Optional[str] = Query(None, description="Filter by status (pending, completed, missed)"),
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter(Task.student_id == current_user.id)
    
    if date:
        query = query.filter(Task.planned_date == date)
    
    if status:
        query = query.filter(Task.status == status)
        
    return query.order_by(Task.created_at.desc()).all()

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.student_id == current_user.id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = task_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(task, key, value)
        
    db.commit()
    db.refresh(task)
    return task

@router.get("/summary")
def get_task_summary(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Auto-update missed tasks before fetching summary
    # Logic: If task is pending and planned_date < today -> mark as missed
    today = date.today()
    missed_tasks = db.query(Task).filter(
        Task.student_id == current_user.id,
        Task.status == "pending",
        Task.planned_date < today
    ).all()
    
    for task in missed_tasks:
        task.status = "missed"
        # Optional: Auto carry forward logic could go here or be a separate action
    
    if missed_tasks:
        db.commit()

    total = db.query(Task).filter(Task.student_id == current_user.id).count()
    completed = db.query(Task).filter(Task.student_id == current_user.id, Task.status == "completed").count()
    pending = db.query(Task).filter(Task.student_id == current_user.id, Task.status == "pending").count()
    missed = db.query(Task).filter(Task.student_id == current_user.id, Task.status == "missed").count()
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "missed": missed
    }
