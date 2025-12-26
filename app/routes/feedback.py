from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..dependencies import get_db, require_admin, require_manager, require_employee

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

# simple abusive words list
ABUSIVE = {"badword", "idiot", "stupid"}


def is_abusive(text: str) -> bool:
    """
    Checks if a given text contains any abusive words from a predefined list.
    This is a simple content moderation function.
    """
    t = text.lower()
    return any(w in t for w in ABUSIVE)


@router.get("/", response_model=List[schemas.FeedbackOut])
def get_all_feedback(db: Session = Depends(get_db), current_user: models.User = Depends(require_manager)):
    """
    Retrieves all feedback for all users.
    Only accessible by Admins and Managers.
    """
    return db.query(models.Feedback).all()


@router.post("", response_model=schemas.FeedbackOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
@router.post("/", response_model=schemas.FeedbackOut, status_code=status.HTTP_201_CREATED)
def post_feedback(
    data: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_employee)
):
    """
    Allows any authenticated user to submit feedback for another user.
    """
    if not data.message.strip():
        raise HTTPException(status_code=400, detail="Feedback message cannot be empty")
    if is_abusive(data.message):
        raise HTTPException(status_code=400, detail="Abusive content is not allowed")

    from_user_id = None if data.is_anonymous else current_user.id
    
    feedback = models.Feedback(
        from_user_id=from_user_id,
        to_user_id=data.to_user_id,
        message=data.message,
        is_anonymous=data.is_anonymous
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.put("/{feedback_id}/approve", response_model=schemas.FeedbackOut)
def approve_feedback(
    feedback_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(require_manager)
):
    """
    Approves a feedback entry. Only accessible by Admins and Managers.
    """
    feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    feedback.status = "approved"
    db.commit()
    db.refresh(feedback)
    return feedback


@router.put("/{feedback_id}/reject", response_model=schemas.FeedbackOut)
def reject_feedback(
    feedback_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(require_manager)
):
    """
    Rejects a feedback entry. Only accessible by Admins and Managers.
    """
    feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    feedback.status = "rejected"
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/me", response_model=List[schemas.FeedbackOut])
def get_my_feedback(db: Session = Depends(get_db), current_user: models.User = Depends(require_employee)):
    """
    Retrieves all feedback received by the currently logged-in user.
    """
    feedback_list = db.query(models.Feedback).filter(models.Feedback.to_user_id == current_user.id).all()
    return feedback_list


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_d),
    current_user: models.User = Depends(require_admin)
):
    """
    Deletes a feedback entry. Only accessible by Admins.
    """
    feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    db.delete(feedback)
    db.commit()
    return {"detail": "Feedback deleted successfully"}
