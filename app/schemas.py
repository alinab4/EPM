from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


class UserBase(BaseModel):
    name: str
    email: EmailStr
    department: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: str = Field("Employee", pattern="^(Admin|Manager|Employee)$")
    manager_id: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(Admin|Manager|Employee)$")
    manager_id: Optional[int] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None



class UserOut(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PerformanceCreate(BaseModel):
    employee_id: int
    rating: float = Field(..., ge=0, le=5)
    comments: Optional[str] = None


class PerformanceOut(BaseModel):
    id: int
    employee_id: int
    manager_id: int
    rating: float
    comments: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackCreate(BaseModel):
    to_user_id: int
    message: str
    is_anonymous: bool = False


class FeedbackOut(BaseModel):
    id: int
    from_user_id: Optional[int] = None
    to_user_id: int
    message: str
    is_anonymous: bool
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KPICreate(BaseModel):
    title: str
    target: float
    weightage: float = 1.0
    department: Optional[str] = None


class KPIOut(BaseModel):
    id: int
    title: str
    target: float
    weightage: float
    department: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class KPIEvaluate(BaseModel):
    kpi_id: int
    employee_id: int
    achieved_value: float


class KPIResultBase(BaseModel):
    kpi_id: int
    employee_id: int
    achieved_value: float
    status: str
    score: float


class KPIResultOut(KPIResultBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class ApprovalCreate(BaseModel):
    user_id: int
    type: str


class ApprovalOut(BaseModel):
    id: int
    user_id: int
    type: str
    status: str
    approved_by: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeDashboard(BaseModel):
    average_performance: float
    feedback_count: int
    latest_rating: Optional[float] = None
    reviews: List[PerformanceOut]


class AdminDashboard(BaseModel):
    total_employees: int
    average_performance: float
    feedback_count: int
    latest_rating: Optional[float] = None
    kpi_achievement_percent: float


class ManagerDashboard(BaseModel):
    team_size: int
    average_performance: float
    feedback_count: int
    latest_rating: Optional[float] = None
