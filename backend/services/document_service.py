import os
import shutil
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from backend.models.models import Document

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

def get_document(db: Session, document_id: int) -> Optional[Document]:
    return db.query(Document).filter(Document.id == document_id).first()

def get_documents_by_employee(db: Session, employee_id: int) -> List[Document]:
    return db.query(Document).filter(Document.employee_id == employee_id).all()

def create_document(db: Session, title: str, file: UploadFile, employee_id: int) -> Document:
    # Ensure the upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename/path
    filename = f"{employee_id}_{int(os.path.getmtime(UPLOAD_DIR))}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save the file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Save metadata to DB
    db_document = Document(
        title=title,
        file_path=file_path,
        file_type=file.content_type,
        employee_id=employee_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def delete_document(db: Session, db_document: Document) -> bool:
    # Delete the physical file from disk if it exists
    if os.path.exists(db_document.file_path):
        try:
            os.remove(db_document.file_path)
        except Exception:
            # Keep deleting DB entry even if disk file delete fails
            pass
            
    # Delete DB entry
    db.delete(db_document)
    db.commit()
    return True
