from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, models, auth
from ..dependencies import get_db, get_current_user, require_roles, require_admin

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 password flow for login. Returns JWT token."""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = auth.create_access_token({"user_id": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user. This is a public endpoint for self-registration.
    New users will default to the 'Employee' role.
    """
    if db.query(models.User).filter(models.User.email == new_user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(new_user.password)
    
    user = models.User(
        name=new_user.name,
        email=new_user.email,
        password_hash=hashed_password,
        role=new_user.role or "Employee",  # Ensure default role
        department=new_user.department,
        manager_id=new_user.manager_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
