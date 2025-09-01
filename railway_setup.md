# Railway Database Setup Guide

## The Problem
Your application is getting "database not available" errors because Railway doesn't provide MySQL by default, and the database connection isn't configured.

## Solution 1: Use Railway's PostgreSQL (Recommended)

### Step 1: Add PostgreSQL Service
1. Go to your Railway project dashboard
2. Click "New Service" → "Database" → "PostgreSQL"
3. Wait for it to provision

### Step 2: Update Environment Variables
Railway will automatically add these environment variables to your app service:
- `DATABASE_URL` (PostgreSQL connection string)
- `PGHOST`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`
- `PGPORT`

### Step 3: Update Your App
Add this to your `.env` file on Railway:
```
DB_TYPE=postgresql
DB_HOST=${PGHOST}
DB_NAME=${PGDATABASE}
DB_USER=${PGUSER}
DB_PASSWORD=${PGPASSWORD}
DB_PORT=${PGPORT}
```

## Solution 2: Use External MySQL Service

### Option A: PlanetScale (Free Tier)
1. Go to [planetscale.com](https://planetscale.com)
2. Create account and database
3. Get connection details
4. Add to Railway environment variables

### Option B: Railway MySQL Plugin
1. Install Railway MySQL plugin
2. Provision MySQL service
3. Configure environment variables

## Solution 3: Quick Fix for Testing

If you just want to test the app without a database, you can temporarily disable database requirements:

```python
# In app.py, temporarily set:
self.db_available = True  # Skip database setup
```

## Current Status
- ✅ App is deployed and running
- ❌ Database connection not configured
- ❌ User registration failing

## Next Steps
1. **Choose a database solution** (PostgreSQL recommended)
2. **Provision the database service**
3. **Update environment variables**
4. **Redeploy your app**

## Environment Variables Needed
```
# Database
DB_TYPE=postgresql  # or mysql
DB_HOST=your-db-host
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_PORT=5432  # or 3306 for MySQL

# Other required
SECRET_KEY=your-secret-key
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-app-password
HUGGINGFACE_API_KEY=your-api-key
```

## Testing
After setup, test the signup page again at:
https://eduverseai.up.railway.app/signup

The "database not available" error should be resolved.
