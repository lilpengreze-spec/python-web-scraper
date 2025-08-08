@echo off
REM Git Repository Setup Script for Review Scraper (Windows)
REM Run this script after installing Git to initialize your repository

echo 🚀 Setting up Git repository for Review Scraper...

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git is not installed or not in PATH
    echo Please install Git from: https://git-scm.com/download/windows
    echo Or use GitHub Desktop: https://desktop.github.com
    pause
    exit /b 1
)

REM Initialize repository if not already initialized
if not exist ".git" (
    echo 📁 Initializing Git repository...
    git init
) else (
    echo ✅ Git repository already initialized
)

REM Add all files
echo 📄 Adding files to Git...
git add .

REM Check if there are any changes to commit
git diff --staged --quiet
if %ERRORLEVEL% NEQ 0 (
    echo 💾 Committing files...
    git commit -m "Initial commit: Review Scraper for Yelp and Amazon" -m "Features:" -m "- Production-ready Flask API" -m "- Yelp and Amazon review scraping" -m "- Comprehensive error handling" -m "- Railway deployment ready" -m "- Real-time data fetching" -m "- Background scraping with intervals"
) else (
    echo ℹ️  No changes to commit
)

echo.
echo 🎉 Git repository setup complete!
echo.
echo Next steps:
echo 1. Create a GitHub repository at: https://github.com/new
echo 2. Copy the repository URL
echo 3. Run: git remote add origin ^<your-repo-url^>
echo 4. Run: git branch -M main
echo 5. Run: git push -u origin main
echo.
echo Then deploy to Railway:
echo 1. Go to https://railway.app
echo 2. Click 'Start a New Project'
echo 3. Select 'Deploy from GitHub repo'
echo 4. Choose your repository
echo 5. Deploy automatically!
echo.
echo For detailed instructions, see DEPLOYMENT.md
echo.
pause
