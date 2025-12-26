from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..dependencies import get_db, require_admin, require_manager, require_employee


router = APIRouter(prefix="/api/performance", tags=["performance"])


@router.post("/", response_model=schemas.PerformanceOut)
def create_performance_review(
    review_in: schemas.PerformanceCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(require_manager)
):
    """
    Creates a new performance review. Only accessible by Managers and Admins.
    A manager can only review an employee they manage. An admin can review anyone.
    """
    employee = db.query(models.User).filter(models.User.id == review_in.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Security check: Managers can only review their own team members
    if current_user.role == "Manager" and employee.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only review your own team members")

    review = models.PerformanceReview(
        employee_id=review_in.employee_id,
        manager_id=current_user.id,
        rating=review_in.rating,
        comments=review_in.comments
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/me", response_model=List[schemas.PerformanceOut])
def get_my_performance_reviews(db: Session = Depends(get_db), current_user: models.User = Depends(require_employee)):
    """
    Gets all performance reviews for the currently logged-in user.
    Accessible by any authenticated user.
    """
    reviews = db.query(models.PerformanceReview).filter(models.PerformanceReview.employee_id == current_user.id).all()
    return reviews


@router.get("/employee/{employee_id}", response_model=List[schemas.PerformanceOut])
def get_employee_performance_reviews(employee_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_manager)):
    """
    Gets all performance reviews for a specific employee.
    Accessible by Managers (for their team) and Admins (for anyone).
    """
    employee = db.query(models.User).filter(models.User.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if current_user.role == "Manager" and employee.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view reviews for your own team members")

    reviews = db.query(models.PerformanceReview).filter(models.PerformanceReview.employee_id == employee_id).all()
    return reviews

@router.get("/", response_model=List[schemas.PerformanceOut])
def get_all_performance_reviews(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    """
    Gets all performance reviews in the system.
    Only accessible by Admins.
    """
    return db.query(models.PerformanceReview).all()
