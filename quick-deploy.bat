@echo off
echo ========================================
echo    EduVerse Quick Deploy to Railway
echo ========================================
echo.

echo Step 1: Pushing to GitHub...
git add .
git commit -m "Deploy to Railway"
git push

echo.
echo Step 2: Deploying to Railway...
echo Please go to https://railway.app/dashboard
echo 1. Create new project
echo 2. Deploy from GitHub repo
echo 3. Add MySQL database
echo 4. Set environment variables
echo 5. Deploy!

echo.
echo Your app will be deployed automatically!
pause
