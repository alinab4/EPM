from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="Employee")
    department = Column(String, nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    manager = relationship("User", remote_side=[id])
    performance_reviews = relationship("PerformanceReview", foreign_keys="[PerformanceReview.employee_id]", back_populates="employee")
    manager_reviews = relationship("PerformanceReview", foreign_keys="[PerformanceReview.manager_id]", back_populates="manager")
    feedback_received = relationship("Feedback", foreign_keys="[Feedback.to_user_id]")
    feedback_given = relationship("Feedback", foreign_keys="[Feedback.from_user_id]")
    kpi_results = relationship("KPIResult", back_populates="employee")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', role='{self.role}')>"


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"))
    manager_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Float, nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("User", foreign_keys=[employee_id], back_populates="performance_reviews")
    manager = relationship("User", foreign_keys=[manager_id], back_populates="manager_reviews")


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class Approval(Base):
    __tablename__ = "approvals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    status = Column(String, default="pending")
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class KPI(Base):
    __tablename__ = "kpis"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    target = Column(Float, nullable=False)
    weightage = Column(Float, default=1.0)
    department = Column(String, nullable=True)


class KPIResult(Base):
    __tablename__ = "kpi_results"
    id = Column(Integer, primary_key=True, index=True)
    kpi_id = Column(Integer, ForeignKey("kpis.id"))
    employee_id = Column(Integer, ForeignKey("users.id"))
    achieved_value = Column(Float, nullable=False)
    status = Column(String)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("User", back_populates="kpi_results")
    kpi = relationship("KPI")
