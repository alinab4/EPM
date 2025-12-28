# ⚠️ CRITICAL: Railway Database Setup

## The Issue
Your application is failing because **PostgreSQL is not connected to your Railway project**.

The error shows:
```
connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

This means the app is looking for a local database (on your computer), not the Railway database.

---

## ✅ Solution: Add PostgreSQL to Railway

### Step 1: Go to Your Railway Project
1. Open [railway.app](https://railway.app)
2. Click on your project: **web-production-3b871**

### Step 2: Add PostgreSQL Database
1. Click the **"New"** button (top right corner)
2. Select **"Database"**
3. Click **"PostgreSQL"**
4. Wait 1-2 minutes for provisioning

### Step 3: Verify DATABASE_URL
1. Click on the **"postgresql"** service that was just created
2. Go to the **"Variables"** tab
3. You should see `DATABASE_URL` with a value like:
   ```
   postgresql://user:password@host:port/database
   ```

### Step 4: Trigger Redeploy
1. Go back to your **"web"** service
2. Click **"Deployments"**
3. Click the "..." menu on the latest deployment
4. Click **"Redeploy"** (this will use the new DATABASE_URL)
5. Wait for the deployment to complete (green checkmark)

---

## 🔍 Verify the Fix

Once Railway redeploys:

1. **Open the diagnostics page:**
   ```
   https://your-railway-url/diagnostics.html
   ```

2. **Click "Check API Health"**
   - Should show: `✅ API Response: {"status": "healthy", "database": "connected"}`

3. **Try logging in:**
   - Email: `admin@example.com`
   - Password: `adminpass`

---

## ❌ If It's Still Failing

Check these:

### 1. Did PostgreSQL Add-on Install?
- In Railway, you should see **2 services**:
  - `web` (your FastAPI app)
  - `postgresql` (the database)

If only `web` exists, PostgreSQL didn't install. Try again.

### 2. Check Environment Variables
In your `web` service's Variables tab:
- You should see `DATABASE_URL` (auto-added by Railway)
- **Do NOT manually set** `DB_HOST`, `DB_USER`, `DB_PASSWORD` - these will override the `DATABASE_URL`

### 3. Clear Old Variables
If you have these variables, **DELETE THEM**:
- `DB_HOST=localhost` ← **REMOVE**
- `DB_USER=epm_user` ← **REMOVE**
- `DB_PASSWORD=epm_password` ← **REMOVE**

They cause the app to ignore `DATABASE_URL` and try to connect to localhost.

### 4. Check Logs
In your Railway project:
1. Click on **"web"** service
2. Go to **"Logs"** or **"Deploy Logs"**
3. Look for: `✗ Warning: Could not initialize database`

If you see this, the `DATABASE_URL` is still not set.

---

## 🚀 Quick Checklist

- [ ] PostgreSQL add-on installed in Railway
- [ ] `DATABASE_URL` exists in Variables tab
- [ ] Old `DB_*` variables deleted
- [ ] Redeployed the web service
- [ ] Logs show: `✓ Database initialized successfully`
- [ ] Diagnostics page shows: `✅ database: connected`
- [ ] Can login with `admin@example.com` / `adminpass`

---

## 📝 Sample Data
After first successful connection, these users are auto-created:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | adminpass |
| Manager | manager@example.com | managerpass |
| Employee | john.smith@example.com | password123 |
| (+ 7 more employees) | - | password123 |

---

## 🆘 Still Having Issues?

1. **Share the output from the diagnostics page** (https://your-url/diagnostics.html)
2. **Show the Railway logs** (from Deploy Logs or Runtime Logs tab)
3. **Tell me what you see** when you click "Test Login"

Once I see these details, I can provide the exact fix!

