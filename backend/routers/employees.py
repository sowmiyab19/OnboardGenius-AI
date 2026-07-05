from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeDetailResponse
from backend.services import employee_service, user_service
from backend.auth.auth import require_hr, get_current_user
from backend.models.models import User

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_new_employee(
    employee_data: EmployeeCreate, 
    db: Session = Depends(get_db), 
    hr: User = Depends(require_hr)
):
    # If a user ID is specified, check that the user exists and does not already have an employee profile
    if employee_data.user_id:
        user = user_service.get_user(db, user_id=employee_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        existing_profile = employee_service.get_employee_by_user_id(db, user_id=employee_data.user_id)
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Employee profile already exists for this user"
            )
    return employee_service.create_employee(db, employee=employee_data)

@router.get("/", response_model=List[EmployeeResponse])
def read_all_employees(
    department: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    hr: User = Depends(require_hr)
):
    return employee_service.get_employees(db, department=department, status=status, skip=skip, limit=limit)

@router.get("/{employee_id}", response_model=EmployeeDetailResponse)
def read_employee_by_id(
    employee_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_employee = employee_service.get_employee(db, employee_id=employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Employee profile not found"
        )
    # Authorization: check if admin/hr OR if employee is viewing their own profile
    if current_user.role not in ["admin", "hr"] and db_employee.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this profile"
        )
    return db_employee

@router.get("/user/{user_id}", response_model=EmployeeDetailResponse)
def read_employee_by_user_id(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Authorization: check if admin/hr OR if employee is viewing their own profile
    if current_user.role not in ["admin", "hr"] and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this profile"
        )
    db_employee = employee_service.get_employee_by_user_id(db, user_id=user_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Employee profile not found"
        )
    return db_employee

@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee_by_id(
    employee_id: int, 
    employee_update: EmployeeUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_employee = employee_service.get_employee(db, employee_id=employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Employee profile not found"
        )
    # Authorization: admin/hr can edit anything. Employees can only update their own contact info (first/last name, phone)
    is_hr = current_user.role in ["admin", "hr"]
    is_self = db_employee.user_id == current_user.id
    
    if not is_hr and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this profile"
        )
        
    if not is_hr:
        # Prevent employees from changing department, position, hire date, status or user_id mapping
        employee_update.department = None
        employee_update.position = None
        employee_update.hire_date = None
        employee_update.onboarding_status = None
        
    return employee_service.update_employee(db, db_employee=db_employee, employee_update=employee_update)

@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
def delete_employee_by_id(
    employee_id: int, 
    db: Session = Depends(get_db), 
    hr: User = Depends(require_hr)
):
    db_employee = employee_service.get_employee(db, employee_id=employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Employee profile not found"
        )
    employee_service.delete_employee(db, db_employee=db_employee)
    return {"detail": "Employee profile successfully deleted"}
