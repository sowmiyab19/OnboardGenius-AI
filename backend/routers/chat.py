from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas import ChatHistoryResponse
from backend.services import chat_service, ai_service, employee_service, document_service, task_service
from backend.auth.auth import get_current_user, require_hr
from backend.models.models import User
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["Chatbot & AI"])

# Request Schemas
class ChatQueryRequest(BaseModel):
    message: str

class RecommendTasksRequest(BaseModel):
    position: str
    department: str

class GenerateEmailRequest(BaseModel):
    email_type: str  # e.g., 'welcome', 'equipment'
    details: Dict[str, Any]

@router.post("/query", response_model=ChatHistoryResponse)
def query_chatbot(
    request: ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty"
        )
        
    # Gather context information
    context_data = {}
    emp = employee_service.get_employee_by_user_id(db, user_id=current_user.id)
    if emp:
        context_data["name"] = f"{emp.first_name} {emp.last_name}"
        context_data["department"] = emp.department
        context_data["position"] = emp.position
        
        # Get tasks context
        tasks = task_service.get_tasks_by_employee(db, employee_id=emp.id)
        task_lines = []
        for t in tasks:
            task_lines.append(f"- {t.title} [Status: {t.status}, Due: {t.due_date}]")
        context_data["tasks_info"] = "\n".join(task_lines) if task_lines else "No tasks assigned."

    # Generate bot response
    response_text = chat_service.generate_chatbot_response(message=request.message, context=context_data)
    
    # Log to database
    chat_log = chat_service.log_chat_message(
        db, 
        user_id=current_user.id, 
        message=request.message, 
        response=response_text
    )
    return chat_log

@router.post("/summarize/{document_id}", response_model=ChatHistoryResponse)
def summarize_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch Document
    doc = document_service.get_document(db, document_id=document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    # Check permissions (must own document or be HR)
    emp = employee_service.get_employee(db, employee_id=doc.employee_id)
    if current_user.role not in ["admin", "hr"] and (not emp or emp.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this document"
        )
        
    # Generate summary
    summary_text = ai_service.summarize_document(doc.file_path)
    
    # Log to chat history
    query_message = f"Summarize document: {doc.title}"
    chat_log = chat_service.log_chat_message(
        db,
        user_id=current_user.id,
        message=query_message,
        response=summary_text
    )
    return chat_log

@router.post("/recommend-tasks")
def recommend_tasks(
    request: RecommendTasksRequest,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr)
):
    recommendations = ai_service.recommend_tasks_by_job(
        position=request.position, 
        department=request.department
    )
    return {"recommendations": recommendations}

@router.post("/generate-email")
def generate_email(
    request: GenerateEmailRequest,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr)
):
    email_draft = ai_service.generate_onboarding_email(
        email_type=request.email_type,
        details=request.details
    )
    return {"email": email_draft}

@router.get("/history", response_model=List[ChatHistoryResponse])
def get_user_chat_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return chat_service.get_chat_history(db, user_id=current_user.id, skip=skip, limit=limit)
