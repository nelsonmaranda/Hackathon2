@echo off
echo 🚀 EduVerse Railway Deployment Script
echo ===================================

REM Check if Railway CLI is installed
railway --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Railway CLI not found. Installing...
    npm install -g @railway/cli
) else (
    echo ✅ Railway CLI is already installed
)

REM Check if user is logged in
railway whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 Please login to Railway...
    railway login
) else (
    echo ✅ Already logged in to Railway
)

REM Initialize Railway project if not already done
if not exist ".railway" (
    echo 🚂 Initializing Railway project...
    railway init
) else (
    echo ✅ Railway project already initialized
)

REM Deploy the application
echo 🚀 Deploying to Railway...
railway up

echo.
echo 🎉 Deployment completed!
echo 📱 Your app should now be live on Railway!
echo 🔗 Check your Railway dashboard for the live URL
echo.
echo 📋 Next steps:
echo 1. Set up your environment variables in Railway dashboard
echo 2. Configure your MySQL database
echo 3. Add your Hugging Face API key
echo 4. Test your application!

pause
