from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db, SessionLocal
from . import models
from .routes import auth, users, performance, feedback, kpi
from .ngrok import init_ngrok, shutdown_ngrok
import os

app = FastAPI(title="Employee Performance Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(performance.router)
app.include_router(feedback.router)
app.include_router(kpi.router)

# Mount frontend static directory AFTER API routes so /api/* paths match first
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.on_event("startup")
def on_startup():
    """Initialize DB, create sample data, and start ngrok on startup"""
    from .auth import get_password_hash
    from datetime import datetime, timedelta
    import random
    
    init_db()
    
    db = SessionLocal()
    try:
        # Define a helper function to create users and avoid code duplication
        def create_user_if_not_exists(name, email, password, role, department, manager_id=None):
            user = db.query(models.User).filter(models.User.email == email).first()
            if not user:
                user = models.User(
                    name=name,
                    email=email,
                    password_hash=get_password_hash(password),
                    role=role,
                    department=department,
                    manager_id=manager_id,
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"✓ Created {role}: {name}")
            return user

        # --- Create Admins ---
        admin1 = create_user_if_not_exists("Admin User", "admin@example.com", "adminpass", "Admin", "HR")
        admin2 = create_user_if_not_exists("Super Admin", "admin2@example.com", "adminpass2", "Admin", "IT")

        # --- Create Managers ---
        manager1 = create_user_if_not_exists("Manager User", "manager@example.com", "managerpass", "Manager", "Sales")
        manager2 = create_user_if_not_exists("Senior Manager", "manager2@example.com", "managerpass2", "Manager", "Engineering")

        # --- Create Employees ---
        # Get managers to assign employees to them
        managers = [manager1, manager2]
        
        employee_data = [
            ("John Smith", "john.smith@example.com", "Engineering"),
            ("Sarah Johnson", "sarah.johnson@example.com", "Marketing"),
            ("Michael Chen", "michael.chen@example.com", "Engineering"),
            ("Emma Wilson", "emma.wilson@example.com", "HR"),
            ("David Brown", "david.brown@example.com", "Sales"),
            ("Lisa Anderson", "lisa.anderson@example.com", "Product"),
            ("James Miller", "james.miller@example.com", "Engineering"),
            ("Rachel Davis", "rachel.davis@example.com", "Marketing"),
            ("Peter Jones", "peter.jones@example.com", "Sales"),
            ("Olivia Garcia", "olivia.garcia@example.com", "Product"),
        ]

        for name, email, dept in employee_data:
            # Assign employees to managers in a round-robin fashion
            assigned_manager = random.choice(managers)
            create_user_if_not_exists(name, email, "password123", "Employee", dept, manager_id=assigned_manager.id)
        
        # --- Create sample performance reviews ---
        all_employees = db.query(models.User).filter(models.User.role == "Employee").all()
        all_managers = db.query(models.User).filter(models.User.role == "Manager").all()

        if all_managers and all_employees:
            for employee in all_employees:
                # Find the employee's manager
                manager = db.query(models.User).filter(models.User.id == employee.manager_id).first()
                if not manager:
                    manager = random.choice(all_managers) # Assign a random manager if not set

                existing_review = db.query(models.PerformanceReview).filter(
                    models.PerformanceReview.employee_id == employee.id,
                    models.PerformanceReview.manager_id == manager.id
                ).first()
                
                if not existing_review:
                    review = models.PerformanceReview(
                        employee_id=employee.id,
                        manager_id=manager.id,
                        rating=round(random.uniform(2.5, 5.0), 1),
                        comments=random.choice([
                            "Great performance! Keep it up.",
                            "Good work overall. Minor improvements needed.",
                            "Excellent contribution to the team.",
                            "Solid performer with strong potential.",
                            "Meeting expectations. Continue development.",
                            "Outstanding work this quarter!"
                        ]),
                        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                    )
                    db.add(review)
            
            db.commit()
            print(f"✓ Created sample performance reviews")
        
        # --- Create sample feedback ---
        if len(all_employees) >= 2:
            for i in range(min(10, len(all_employees) * 2)):
                feedback_from = random.choice(all_employees)
                feedback_to = random.choice([u for u in all_employees if u.id != feedback_from.id])
                
                existing_feedback = db.query(models.Feedback).filter(
                    models.Feedback.from_user_id == feedback_from.id,
                    models.Feedback.to_user_id == feedback_to.id
                ).first()
                
                if not existing_feedback:
                    feedback_obj = models.Feedback(
                        from_user_id=feedback_from.id,
                        to_user_id=feedback_to.id,
                        message=random.choice([
                            "Great teamwork on the recent project!",
                            "Your communication skills are excellent.",
                            "Keep up the good work!",
                            "Your attention to detail is appreciated.",
                            "Excellent problem-solving abilities.",
                            "Great initiative and leadership!",
                            "Very collaborative and supportive colleague.",
                            "Outstanding technical skills demonstrated."
                        ]),
                        is_anonymous=random.choice([True, False]),
                        status="approved",
                        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                    )
                    db.add(feedback_obj)
            
            db.commit()
            print(f"✓ Created sample feedback")
        
        # --- Create sample KPIs ---
        kpis = [
            {"title": "Sales Target", "target": 100000.0, "weightage": 1.5, "dept": "Sales"},
            {"title": "Code Quality Score", "target": 95.0, "weightage": 1.0, "dept": "Engineering"},
            {"title": "Customer Satisfaction", "target": 90.0, "weightage": 1.2, "dept": None},
            {"title": "Project Completion Rate", "target": 100.0, "weightage": 1.0, "dept": None},
            {"title": "Team Engagement Score", "target": 85.0, "weightage": 0.8, "dept": None},
            {"title": "Marketing Campaign ROI", "target": 300.0, "weightage": 1.3, "dept": "Marketing"},
        ]
        
        for kpi_data in kpis:
            existing_kpi = db.query(models.KPI).filter(models.KPI.title == kpi_data["title"]).first()
            if not existing_kpi:
                kpi = models.KPI(
                    title=kpi_data["title"],
                    target=kpi_data["target"],
                    weightage=kpi_data["weightage"],
                    department=kpi_data["dept"]
                )
                db.add(kpi)
        
        db.commit()
        print(f"✓ Created sample KPIs")
        
        # --- Create sample KPI results ---
        kpis_list = db.query(models.KPI).all()
        if kpis_list and all_employees:
            for kpi in kpis_list:
                for employee in random.sample(all_employees, min(3, len(all_employees))):
                    existing_result = db.query(models.KPIResult).filter(
                        models.KPIResult.kpi_id == kpi.id,
                        models.KPIResult.employee_id == employee.id
                    ).first()
                    
                    if not existing_result:
                        achieved_value = kpi.target * random.uniform(0.7, 1.1)
                        percent = (achieved_value / kpi.target) if kpi.target else 0
                        status = "Achieved" if percent >= 1 else ("Partial" if percent > 0 else "Not Achieved")
                        score = percent * kpi.weightage * 100
                        
                        result = models.KPIResult(
                            kpi_id=kpi.id,
                            employee_id=employee.id,
                            achieved_value=round(achieved_value, 2),
                            status=status,
                            score=round(score, 2),
                            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                        )
                        db.add(result)
            
            db.commit()
            print(f"✓ Created sample KPI results")
            
        print("✓ Database initialized successfully with sample data")
        
    except Exception as e:
        print(f"✗ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


@app.on_event("shutdown")
def on_shutdown():
    """Close ngrok tunnels on shutdown"""
    shutdown_ngrok()

