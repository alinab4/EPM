from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..dependencies import get_db, require_admin, require_manager

router = APIRouter(prefix="/api/kpi", tags=["kpi"])


@router.get("/", response_model=List[schemas.KPIOut])
def get_all_kpis(db: Session = Depends(get_db), current_user: models.User = Depends(require_manager)):
    """
    Retrieves all KPIs. Accessible only by Admins and Managers.
    """
    return db.query(models.KPI).all()


@router.post("/", response_model=schemas.KPIOut)
def create_kpi(kpi_in: schemas.KPICreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    """
    Creates a new KPI. Accessible only by Admins.
    """
    kpi = models.KPI(**kpi_in.dict())
    db.add(kpi)
    db.commit()
    db.refresh(kpi)
    return kpi


@router.post("/evaluate", response_model=schemas.KPIResultOut)
def evaluate_kpi_performance(
    evaluation: schemas.KPIEvaluate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(require_manager)
):
    """
    Evaluates an employee's performance against a specific KPI.
    Accessible by Admins and Managers.
    """
    kpi = db.query(models.KPI).filter(models.KPI.id == evaluation.kpi_id).first()
    employee = db.query(models.User).filter(models.User.id == evaluation.employee_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Security check for managers
    if current_user.role == "Manager" and employee.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only evaluate your own team members")

    percent_achieved = (evaluation.achieved_value / kpi.target) if kpi.target > 0 else 0
    status = "Achieved" if percent_achieved >= 1 else "Not Achieved"
    score = percent_achieved * kpi.weightage * 100

    result = models.KPIResult(
        kpi_id=evaluation.kpi_id,
        employee_id=evaluation.employee_id,
        achieved_value=evaluation.achieved_value,
        status=status,
        score=score
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result
