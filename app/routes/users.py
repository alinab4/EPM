from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..dependencies import get_db, require_admin, require_manager, require_employee, get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


# Any authenticated user can see the list of users.
# The empty string route handles requests to /api/users without a trailing slash.
@router.get("", response_model=List[schemas.UserOut], include_in_schema=False)
@router.get("/", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db), current_user: models.User = Depends(require_employee)):
    users = db.query(models.User).all()
    return users


@router.post("/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # Only admins can create new users
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
    from ..auth import get_password_hash
    user = models.User(
        name=user_in.name, 
        email=user_in.email, 
        password_hash=get_password_hash(user_in.password), 
        role=user_in.role, 
        department=user_in.department, 
        manager_id=user_in.manager_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_in: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # Only admins can update user information
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    update_data = user_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    if user_in.password:
        from ..auth import get_password_hash
        user.password_hash = get_password_hash(user_in.password)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # Only admins can delete users
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}


@router.post("/{user_id}/assign-manager", response_model=schemas.UserOut)
def assign_manager(user_id: int, manager_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # Only admins can assign managers
    user = db.query(models.User).filter(models.User.id == user_id).first()
    manager = db.query(models.User).filter(models.User.id == manager_id, models.User.role == 'Manager').first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not manager:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manager not found or specified user is not a manager")
        
    user.manager_id = manager_id
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/activate", response_model=schemas.UserOut)
def activate_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # Only admins can activate users
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/deactivate", response_model=schemas.UserOut)
def deactivate_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # Only admins can deactivate users
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


# Dashboard endpoints are now role-protected
@router.get("/dashboard/admin", response_model=schemas.AdminDashboard)
def dashboard_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    total_employees = db.query(models.User).count()
    # ... (rest of the dashboard logic remains the same)
    avg_score = db.query(models.PerformanceReview).with_entities(models.PerformanceReview.rating).all()
    ratings = [r[0] for r in avg_score if r[0] is not None]
    avg = sum(ratings) / len(ratings) if ratings else 0
    feedback_count = db.query(models.Feedback).count()
    latest = db.query(models.PerformanceReview).order_by(models.PerformanceReview.created_at.desc()).first()
    latest_rating = latest.rating if latest else None
    kpi_total = db.query(models.KPIResult).count()
    kpi_achieved = db.query(models.KPIResult).filter(models.KPIResult.status == "Achieved").count()
    kpi_percent = (kpi_achieved / kpi_total * 100) if kpi_total else 0
    
    return {
        "total_employees": total_employees, 
        "average_performance": avg, 
        "feedback_count": feedback_count, 
        "latest_rating": latest_rating, 
        "kpi_achievement_percent": kpi_percent
    }


@router.get("/dashboard/manager", response_model=schemas.ManagerDashboard)
def dashboard_manager(db: Session = Depends(get_db), current_user: models.User = Depends(require_manager)):
    # ... (rest of the dashboard logic remains the same)
    team = db.query(models.User).filter(models.User.manager_id == current_user.id).all()
    team_ids = [u.id for u in team]
    reviews = db.query(models.PerformanceReview).filter(models.PerformanceReview.employee_id.in_(team_ids)).all()
    avg = sum([r.rating for r in reviews if r.rating is not None]) / len([r for r in reviews if r.rating is not None]) if reviews else 0
    feedback_count = db.query(models.Feedback).filter(models.Feedback.to_user_id.in_(team_ids)).count()
    latest = db.query(models.PerformanceReview).filter(models.PerformanceReview.employee_id.in_(team_ids)).order_by(models.PerformanceReview.created_at.desc()).first()
    latest_rating = latest.rating if latest else None
    
    return {
        "team_size": len(team), 
        "average_performance": avg, 
        "feedback_count": feedback_count, 
        "latest_rating": latest_rating
    }


@router.get("/dashboard/employee", response_model=schemas.EmployeeDashboard)
def dashboard_employee(db: Session = Depends(get_db), current_user: models.User = Depends(require_employee)):
    # ... (rest of the dashboard logic remains the same)
    reviews = db.query(models.PerformanceReview).filter(models.PerformanceReview.employee_id == current_user.id).all()
    avg = sum([r.rating for r in reviews if r.rating is not None]) / len([r for r in reviews if r.rating is not None]) if reviews else 0
    feedback_count = db.query(models.Feedback).filter(models.Feedback.to_user_id == current_user.id).count()
    latest = db.query(models.PerformanceReview).filter(models.PerformanceReview.employee_id == current_user.id).order_by(models.PerformanceReview.created_at.desc()).first()
    latest_rating = latest.rating if latest else None
    
    return {
        "average_performance": avg,
        "feedback_count": feedback_count,
        "latest_rating": latest_rating,
        "reviews": reviews
    }
