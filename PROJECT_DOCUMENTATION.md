# Project Documentation: Employee Performance Management System

## 1. Introduction
This document provides a comprehensive, in-depth overview of the Employee Performance Management (EPM) system. The EPM system is a web-based application designed to streamline and automate the process of performance reviews, feedback, and KPI tracking within an organization. It provides a platform for employees, managers, and administrators to interact and manage performance-related activities, with the goal of fostering a culture of continuous improvement and data-driven decision-making.

## 2. System Architecture
The EPM system is built on a modern, decoupled architecture consisting of three main components:

*   **Frontend**: A single-page application (SPA) built with HTML, CSS, and JavaScript that provides a dynamic and responsive user interface.
*   **Backend**: A RESTful API built with Python and FastAPI that handles the business logic, data processing, and security.
*   **Database**: A PostgreSQL database that provides a robust and reliable data storage solution.

This architecture allows for a clear separation of concerns, making the application easier to develop, test, and maintain. It also allows for the frontend and backend to be scaled independently, which is a key advantage for a growing application.

## 3. Frontend

### 3.1. Structure
The frontend is organized into a simple and intuitive file structure:

```
frontend/
├── index.html              # Main entry point for the application
├── login.html              # Login page
├── signup.html             # Signup page
├── employee_dashboard.html # Dashboard for employees
├── manager_dashboard.html  # Dashboard for managers
├── admin_dashboard.html    # Dashboard for administrators
├── style.css               # CSS styles for the application
└── app.js                  # JavaScript code for the application
```

### 3.2. Functionality
The frontend provides a user-friendly interface for interacting with the EPM system. The key functionalities include:

*   **User Authentication**: Users can register, log in, and log out of the application. The frontend handles the storage of JWTs in local storage and includes them in the `Authorization` header of all requests.
*   **Dashboards**: Role-based dashboards for employees, managers, and administrators provide a customized view of the application. These dashboards are dynamically rendered based on the user's role and permissions.
*   **Performance Reviews**: Users can create, view, and manage performance reviews. The frontend provides a rich text editor for writing comments and a rating system for evaluating performance.
*   **Feedback**: Users can give and receive 360-degree feedback. The frontend provides a form for submitting feedback and a view for displaying feedback to the user.
*   **KPI Tracking**: Users can define and track Key Performance Indicators (KPIs). The frontend provides a dashboard for visualizing KPI data and tracking progress over time.

## 4. Backend

### 4.1. API Structure
The backend is a RESTful API built with Python and FastAPI. The API is organized into a modular structure, with each module responsible for a specific set of functionalities.

```
app/
├── main.py         # Main application file
├── database.py     # Database connection and initialization
├── models.py       # SQLAlchemy database models
├── schemas.py      # Pydantic schemas for data validation
├── auth.py         # Authentication and authorization logic
└── routes/
    ├── auth.py     # Authentication endpoints
    ├── users.py    # User management endpoints
    ├── performance.py # Performance review endpoints
    ├── feedback.py # Feedback endpoints
    └── kpi.py      # KPI endpoints
```

### 4.2. Authentication
The application uses JSON Web Tokens (JWT) for authentication. When a user logs in, the server generates a JWT and sends it to the client. The client then includes the JWT in the `Authorization` header of all subsequent requests.

The backend uses role-based access control to restrict access to certain endpoints. The available roles are `Employee`, `Manager`, and `Admin`. This is implemented using FastAPI's dependency injection system.

### 4.3. Database Models
The database schema is defined using SQLAlchemy ORM. The main database models are:

*   `User`: Stores information about users, including their name, email, password, and role.
*   `PerformanceReview`: Stores information about performance reviews.
*   `Feedback`: Stores information about 360-degree feedback.
*   `KPI`: Stores information about Key Performance Indicators.
*   `KPIResult`: Stores the results of KPI tracking.

### 4.4. API Endpoints
The backend provides a comprehensive set of API endpoints for interacting with the EPM system. For a detailed list of all the available endpoints, please refer to the automatically generated API documentation, which is available at `http://127.0.0.1:8000/docs` when the application is running.

## 5. Data Flow
1.  The user interacts with the frontend in their web browser.
2.  The frontend sends HTTP requests to the backend API.
3.  The backend processes the requests, interacts with the PostgreSQL database, and sends back a response.
4.  The frontend receives the response and updates the user interface accordingly.

## 6. Setup and Installation

### Prerequisites
- Python 3.8+
- PostgreSQL

### Installation
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Database Setup
1.  **Create a PostgreSQL database.** The default database name is `epm_db`, but you can choose a different name.
2.  **Configure the database connection** by creating a `.env` file in the project root with the following variables:
    - `DB_USER`
    - `DB_PASSWORD`
    - `DB_HOST`
    - `DB_PORT`
    - `DB_NAME`
3.  **Initialize the database:**
    ```bash
    python setup_backend.py
    ```

### Running the Application
```bash
uvicorn app.main:app --reload
```
The application will be available at `http://127.0.0.1:8000`.
