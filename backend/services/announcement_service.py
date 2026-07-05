from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.models import Announcement
from backend.schemas import AnnouncementCreate, AnnouncementUpdate

def get_announcement(db: Session, announcement_id: int) -> Optional[Announcement]:
    return db.query(Announcement).filter(Announcement.id == announcement_id).first()

def get_announcements(db: Session, skip: int = 0, limit: int = 100) -> List[Announcement]:
    return db.query(Announcement).order_by(Announcement.created_at.desc()).offset(skip).limit(limit).all()

def create_announcement(db: Session, announcement: AnnouncementCreate, creator_id: int) -> Announcement:
    db_announcement = Announcement(
        title=announcement.title,
        content=announcement.content,
        created_by=creator_id
    )
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement

def update_announcement(db: Session, db_announcement: Announcement, announcement_update: AnnouncementUpdate) -> Announcement:
    update_data = announcement_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_announcement, key, value)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement

def delete_announcement(db: Session, db_announcement: Announcement) -> bool:
    db.delete(db_announcement)
    db.commit()
    return True
