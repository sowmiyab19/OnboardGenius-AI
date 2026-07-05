from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.models import Employee
from backend.schemas import EmployeeCreate, EmployeeUpdate

def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.id == employee_id).first()

def get_employee_by_user_id(db: Session, user_id: int) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.user_id == user_id).first()

def get_employees(
    db: Session, 
    department: Optional[str] = None, 
    status: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 100
) -> List[Employee]:
    query = db.query(Employee)
    if department:
        query = query.filter(Employee.department == department)
    if status:
        query = query.filter(Employee.onboarding_status == status)
    return query.offset(skip).limit(limit).all()

def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
    db_employee = Employee(
        user_id=employee.user_id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        phone=employee.phone,
        department=employee.department,
        position=employee.position,
        hire_date=employee.hire_date,
        onboarding_status=employee.onboarding_status or "pending"
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db: Session, db_employee: Employee, employee_update: EmployeeUpdate) -> Employee:
    update_data = employee_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def delete_employee(db: Session, db_employee: Employee) -> bool:
    db.delete(db_employee)
    db.commit()
    return True
