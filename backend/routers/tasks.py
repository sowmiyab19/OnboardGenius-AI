from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas import TaskCreate, TaskUpdate, TaskResponse
from backend.services import task_service, employee_service
from backend.auth.auth import require_hr, get_current_user
from backend.models.models import User

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_new_task(
    task_data: TaskCreate, 
    db: Session = Depends(get_db), 
    hr: User = Depends(require_hr)
):
    # Verify employee exists
    employee = employee_service.get_employee(db, employee_id=task_data.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target employee profile not found"
        )
    return task_service.create_task(db, task=task_data, creator_id=hr.id)

@router.get("/", response_model=List[TaskResponse])
def read_all_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr)
):
    return task_service.get_tasks(db, skip=skip, limit=limit)

@router.get("/employee/{employee_id}", response_model=List[TaskResponse])
def read_tasks_for_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify employee exists
    employee = employee_service.get_employee(db, employee_id=employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    # Check authorization: admin/hr OR employee viewing their own tasks
    if current_user.role not in ["admin", "hr"] and employee.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view these tasks"
        )
    return task_service.get_tasks_by_employee(db, employee_id=employee_id)

@router.get("/{task_id}", response_model=TaskResponse)
def read_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_task = task_service.get_task(db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    # Verify authorization
    employee = employee_service.get_employee(db, employee_id=db_task.employee_id)
    if current_user.role not in ["admin", "hr"] and (not employee or employee.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task"
        )
    return db_task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task_by_id(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_task = task_service.get_task(db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
        
    employee = employee_service.get_employee(db, employee_id=db_task.employee_id)
    is_hr = current_user.role in ["admin", "hr"]
    is_self = employee and employee.user_id == current_user.id
    
    if not is_hr and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this task"
        )
        
    if not is_hr:
        # Employees can only update task status, not title, details, due_date, or assignee
        task_update.title = None
        task_update.description = None
        task_update.due_date = None
        task_update.employee_id = None
        
    return task_service.update_task(db, db_task=db_task, task_update=task_update)

@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr)
):
    db_task = task_service.get_task(db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    task_service.delete_task(db, db_task=db_task)
    return {"detail": "Task successfully deleted"}
