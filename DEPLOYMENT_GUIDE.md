# EPM Application Deployment & Setup Guide

## Quick Start (Local Development)

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 16+ (or SQLite for quick testing)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/alinab4/EPM.git
cd EPM
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source .venv/bin/activate  # Linux/Mac
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Step 5: Start PostgreSQL (if using)
**Windows:**
```bash
net start postgresql-x64-16
```

**Linux/Mac:**
```bash
brew services start postgresql
```

### Step 6: Run the Application
```bash
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`

- **API Docs:** http://127.0.0.1:8000/docs
- **Frontend:** http://127.0.0.1:8000/

---

## Production Deployment (Railway)

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

### Step 2: Create Railway Project
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `alinab4/EPM` repository
4. Wait for automatic build and deployment

### Step 3: Configure Environment Variables
In your Railway project's "Variables" tab, add:

```
USE_SQLITE=false
SECRET_KEY=<generate-a-strong-key>
DB_USER=postgres
DB_PASSWORD=<your-password>
DB_HOST=<railway-database-host>
DB_PORT=5432
DB_NAME=epm_db
```

⚠️ **IMPORTANT:** Railway automatically provides `DATABASE_URL` when you add PostgreSQL!

### Step 4: Add PostgreSQL Database
1. In your Railway project, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically provision and connect the database
3. The `DATABASE_URL` variable will be auto-populated

### Step 5: Deploy
Railway auto-deploys when you push to GitHub. Monitor the "Deploy Logs" tab.

---

## Troubleshooting

### Issue: "Connection refused" on localhost:5432
**Solution:** Start PostgreSQL service
```bash
# Windows
net start postgresql-x64-16

# Linux
sudo systemctl start postgresql

# Mac
brew services start postgresql
```

### Issue: "Database URL not set" on Railway
**Solution:** Ensure PostgreSQL add-on is installed and `DATABASE_URL` appears in Variables tab

### Issue: "Invalid token" login errors
**Solution:** Clear browser localStorage and try again
```javascript
// In browser console
localStorage.clear()
```

### Issue: "Role pattern validation failed" in signup
**Solution:** This is now fixed. Ensure you're using the latest code with `git pull`

---

## Default Test Credentials

After first startup, sample data is auto-created:

**Admin:**
- Email: `admin@example.com`
- Password: `adminpass`

**Manager:**
- Email: `manager@example.com`
- Password: `managerpass`

**Employees:**
- Email: `john.smith@example.com`
- Password: `password123`
- (8 more sample employees created)

---

## Monitoring & Logs

### Local Logs
Watch the terminal where `uvicorn` is running for real-time logs.

### Railway Logs
1. Open your Railway project
2. Click on your application service
3. Go to "Deploy Logs" or "Runtime Logs" tab

---

## API Documentation

Once running, access **Swagger UI** at:
```
http://localhost:8000/docs
```

All endpoints are documented with request/response examples.

---

## Support
For issues, check:
1. The logs (see Monitoring section above)
2. GitHub Issues on the repository
3. Make sure all environment variables are set correctly

---

## Security Notes
1. Change `SECRET_KEY` in production
2. Use strong database passwords
3. Enable HTTPS in production
4. Keep dependencies updated: `pip install --upgrade pip && pip install -r requirements.txt`

