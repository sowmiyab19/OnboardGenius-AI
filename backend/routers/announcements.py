from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
from backend.services import announcement_service
from backend.auth.auth import get_current_user, require_hr
from backend.models.models import User

router = APIRouter(prefix="/announcements", tags=["Announcements"])

@router.post("/", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def create_new_announcement(
    announcement_data: AnnouncementCreate,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr)
):
    return announcement_service.create_announcement(db, announcement=announcement_data, creator_id=hr.id)

@router.get("/", response_model=List[AnnouncementResponse])
def read_all_announcements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return announcement_service.get_announcements(db, skip=skip, limit=limit)

@router.get("/{announcement_id}", response_model=AnnouncementResponse)
def read_announcement_by_id(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_announcement = announcement_service.get_announcement(db, announcement_id=announcement_id)
    if not db_announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    return db_announcement

@router.put("/{announcement_id}", response_model=AnnouncementResponse)
def update_announcement_by_id(
    announcement_id: int,
    announcement_update: AnnouncementUpdate,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr)
):
    db_announcement = announcement_service.get_announcement(db, announcement_id=announcement_id)
    if not db_announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    return announcement_service.update_announcement(db, db_announcement=db_announcement, announcement_update=announcement_update)

@router.delete("/{announcement_id}", status_code=status.HTTP_200_OK)
def delete_announcement_by_id(
    announcement_id: int,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr)
):
    db_announcement = announcement_service.get_announcement(db, announcement_id=announcement_id)
    if not db_announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    announcement_service.delete_announcement(db, db_announcement=db_announcement)
    return {"detail": "Announcement successfully deleted"}
