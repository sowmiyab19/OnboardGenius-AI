from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas import UserCreate, UserUpdate, UserResponse, UserDetailResponse
from backend.services import user_service
from backend.auth.auth import require_admin
from backend.models.models import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    db_user = user_service.get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return user_service.create_user(db=db, user=user_data)

@router.get("/", response_model=List[UserResponse])
def read_all_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    return user_service.get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserDetailResponse)
def read_user_by_id(
    user_id: int, 
    db: Session = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    db_user = user_service.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user_by_id(
    user_id: int, 
    user_update: UserUpdate, 
    db: Session = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    db_user = user_service.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    # If email changes, check uniqueness
    if user_update.email and user_update.email != db_user.email:
        existing_email = user_service.get_user_by_email(db, email=user_update.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    return user_service.update_user(db, db_user=db_user, user_update=user_update)

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_by_id(
    user_id: int, 
    db: Session = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    db_user = user_service.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    if db_user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators cannot delete themselves"
        )
    user_service.delete_user(db, db_user=db_user)
    return {"detail": "User successfully deleted"}
