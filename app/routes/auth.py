from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, models, auth
from ..dependencies import get_db, get_current_user, require_roles, require_admin

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and database connectivity."""
    try:
        # Test database connection
        db.query(models.User).first()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": __import__('datetime').datetime.utcnow()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": __import__('datetime').datetime.utcnow()
        }


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 password flow for login. Returns JWT token."""
    # Try to find user by email (treating username field as email)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # If not found by email, try direct username match
    if not user:
        user = db.query(models.User).filter(models.User.name == form_data.username).first()
    
    # Verify credentials
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not found"
        )
    
    if not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="User account is inactive"
        )
    
    try:
        token = auth.create_access_token({"user_id": user.id, "role": user.role})
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        print(f"✗ Token creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create authentication token"
        )


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user. This is a public endpoint for self-registration.
    New users will default to the 'Employee' role.
    """
    # Validate input
    if not new_user.name or not new_user.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    
    if not new_user.email or not new_user.email.strip():
        raise HTTPException(status_code=400, detail="Email is required")
    
    if not new_user.password or len(new_user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == new_user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        # Hash password
        hashed_password = auth.get_password_hash(new_user.password)
        
        # Determine role (validate it's acceptable)
        role = new_user.role or "Employee"
        if role not in ["Admin", "Manager", "Employee"]:
            role = "Employee"  # Default to Employee if invalid
        
        # Create user
        user = models.User(
            name=new_user.name.strip(),
            email=new_user.email.strip().lower(),
            password_hash=hashed_password,
            role=role,
            department=new_user.department or "",
            manager_id=new_user.manager_id,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✓ User registered successfully: {user.email}")
        return user
        
    except Exception as e:
        db.rollback()
        print(f"✗ Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
