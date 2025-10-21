@echo off
echo 🚀 Preparing Chat2API for Railway deployment...
echo.

echo 📁 Adding files to git...
git add .

echo.
echo 💾 Committing changes...
git commit -m "Add Railway deployment configuration and production settings"

echo.
echo 🚀 Pushing to GitHub...
git push origin main

echo.
echo ✅ Deployment files pushed to GitHub!
echo.
echo 📋 Next steps:
echo 1. Go to https://railway.app
echo 2. Sign up/Login with GitHub
echo 3. Click "New Project" → "Deploy from GitHub repo"
echo 4. Select your Chat2API repository
echo 5. Set environment variables:
echo    - HOST=0.0.0.0
echo    - PORT=8080
echo    - ENABLE_GATEWAY=true
echo    - ENVIRONMENT=production
echo.
echo 🎯 Your Chat2API will be available at: https://your-app-name.railway.app
echo.
pause
