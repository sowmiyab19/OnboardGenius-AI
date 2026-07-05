from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict

# ==========================================
# User Schemas
# ==========================================
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "employee"  # 'admin', 'hr', 'employee'

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# ==========================================
# Employee Schemas
# ==========================================
class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: date
    onboarding_status: Optional[str] = "pending"  # 'pending', 'in_progress', 'completed'

class EmployeeCreate(EmployeeBase):
    user_id: Optional[int] = None

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[date] = None
    onboarding_status: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Task Schemas
# ==========================================
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = "pending"  # 'pending', 'in_progress', 'completed'

class TaskCreate(TaskBase):
    employee_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    employee_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    employee_id: int
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Document Schemas
# ==========================================
class DocumentBase(BaseModel):
    title: str
    file_type: Optional[str] = None
    employee_id: int

class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Announcement Schemas
# ==========================================
class AnnouncementBase(BaseModel):
    title: str
    content: str

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class AnnouncementResponse(AnnouncementBase):
    id: int
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Chat History Schemas
# ==========================================
class ChatHistoryBase(BaseModel):
    message: str
    response: str

class ChatHistoryCreate(ChatHistoryBase):
    pass

class ChatHistoryResponse(ChatHistoryBase):
    id: int
    user_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Nested Relationship Schemas (For detailed fetches)
# ==========================================
class UserDetailResponse(UserResponse):
    employee_profile: Optional[EmployeeResponse] = None

class EmployeeDetailResponse(EmployeeResponse):
    tasks: List[TaskResponse] = []
    documents: List[DocumentResponse] = []
