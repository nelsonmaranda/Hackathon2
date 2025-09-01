# 🚨 Railway Deployment Troubleshooting Guide

## **Error: "Cannot find module '@railway/railway'"**

### **What This Error Means:**
This error occurs when Railway is trying to run your application as a **Node.js application** instead of recognizing it as a **Python Flask application**.

### **Root Causes:**
1. **Runtime Detection Failure**: Railway is not properly detecting Python
2. **Conflicting Configuration**: Multiple deployment configs causing confusion
3. **Build Process Issues**: Nixpacks not properly configured for Python

### **Immediate Fixes Applied:**

#### **1. Enhanced railway.json**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -",
    "healthcheckPath": "/",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### **2. Created nixpacks.toml**
```toml
[phases.setup]
nixPkgs = ["python311", "python311Packages.pip"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -"
```

#### **3. Updated Procfile**
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -
```

#### **4. Added runtime.txt**
```
python-3.11.0
```

### **Deployment Steps (Updated):**

#### **Step 1: Clean Repository**
```bash
# Remove any conflicting files
rm -rf .railway/
rm -f railway.toml

# Commit the new configuration files
git add .
git commit -m "Fix Railway Python runtime detection"
git push
```

#### **Step 2: Redeploy on Railway**
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. **Delete the existing project** (if it exists)
3. Create **new project** → **Deploy from GitHub repo**
4. Select your repository
5. **Wait for build to complete**

#### **Step 3: Verify Python Runtime**
In Railway dashboard, check:
- **Build logs** should show Python installation
- **Runtime** should be detected as Python
- **No Node.js errors** should appear

### **Alternative Deployment Method:**

If the above doesn't work, use **manual deployment**:

#### **Option A: Railway CLI (Local)**
```bash
# Install Railway CLI locally
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

#### **Option B: GitHub Integration Only**
1. **Disable Railway CLI** in your scripts
2. **Rely only on GitHub integration**
3. **Push changes** to trigger auto-deploy

### **Environment Variables Setup:**

Ensure these are set in Railway → Variables:
```
DB_HOST=your-mysql-host
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=eduverse
SECRET_KEY=your-secret-key
FLASK_ENV=production
```

### **Monitoring Deployment:**

#### **Check Build Logs:**
- Look for Python installation messages
- Verify gunicorn is found
- Check for dependency installation

#### **Check Runtime Logs:**
- Should show Flask app starting
- Gunicorn worker processes
- No Node.js module errors

### **If Error Persists:**

#### **1. Force Python Runtime:**
Add to `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  }
}
```

#### **2. Check Dependencies:**
Ensure `requirements.txt` has:
- `gunicorn==21.2.0`
- All Flask dependencies
- No conflicting packages

#### **3. Contact Railway Support:**
- Share build logs
- Mention Python runtime detection issue
- Reference this troubleshooting guide

### **Prevention:**

#### **Best Practices:**
1. **Single Configuration**: Use only one deployment config
2. **Clear Runtime**: Explicitly specify Python version
3. **Clean Repository**: Remove conflicting deployment files
4. **Test Locally**: Verify app runs with gunicorn locally

#### **Local Testing:**
```bash
# Test gunicorn locally
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:8000

# Should start without errors
```

---

## **Summary of Fixes Applied:**

✅ **Enhanced railway.json** with explicit Python configuration  
✅ **Created nixpacks.toml** for Python build process  
✅ **Updated Procfile** with proper gunicorn settings  
✅ **Added runtime.txt** for Python version specification  
✅ **Cleaned requirements.txt** (removed duplicates)  

**Next Step**: Commit these changes, push to GitHub, and redeploy on Railway!
