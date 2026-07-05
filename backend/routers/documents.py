import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas import DocumentResponse
from backend.services import document_service, employee_service
from backend.auth.auth import get_current_user, require_hr
from backend.models.models import User

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    title: str = Form(...),
    employee_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify employee profile exists
    employee = employee_service.get_employee(db, employee_id=employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
        
    # Authorization: admin/hr OR employee uploading for their own profile
    is_hr = current_user.role in ["admin", "hr"]
    is_self = employee.user_id == current_user.id
    
    if not is_hr and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to upload documents for this employee"
        )
        
    return document_service.create_document(db, title=title, file=file, employee_id=employee_id)

@router.get("/employee/{employee_id}", response_model=List[DocumentResponse])
def list_employee_documents(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = employee_service.get_employee(db, employee_id=employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
        
    # Authorization check
    if current_user.role not in ["admin", "hr"] and employee.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view these documents"
        )
        
    return document_service.get_documents_by_employee(db, employee_id=employee_id)

@router.get("/{document_id}/download")
def download_document_file(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_document = document_service.get_document(db, document_id=document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document record not found"
        )
        
    # Authorization check: verify link to employee
    employee = employee_service.get_employee(db, employee_id=db_document.employee_id)
    if current_user.role not in ["admin", "hr"] and (not employee or employee.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to download this document"
        )
        
    if not os.path.exists(db_document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Physical file not found on disk"
        )
        
    return FileResponse(
        path=db_document.file_path,
        filename=os.path.basename(db_document.file_path),
        media_type=db_document.file_type
    )

@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document_record(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_document = document_service.get_document(db, document_id=document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    # Authorization: admin/hr OR employee deleting their own upload
    employee = employee_service.get_employee(db, employee_id=db_document.employee_id)
    is_hr = current_user.role in ["admin", "hr"]
    is_self = employee and employee.user_id == current_user.id
    
    if not is_hr and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this document"
        )
        
    document_service.delete_document(db, db_document=db_document)
    return {"detail": "Document successfully deleted"}
