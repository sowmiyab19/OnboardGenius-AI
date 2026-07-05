from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.models import Task
from backend.schemas import TaskCreate, TaskUpdate

def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks_by_employee(db: Session, employee_id: int) -> List[Task]:
    return db.query(Task).filter(Task.employee_id == employee_id).all()

def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    return db.query(Task).offset(skip).limit(limit).all()

def create_task(db: Session, task: TaskCreate, creator_id: int) -> Task:
    db_task = Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        status=task.status or "pending",
        employee_id=task.employee_id,
        created_by=creator_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, db_task: Task, task_update: TaskUpdate) -> Task:
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, db_task: Task) -> bool:
    db.delete(db_task)
    db.commit()
    return True
