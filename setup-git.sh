#!/bin/bash

# Git Repository Setup Script for Review Scraper
# Run this script after installing Git to initialize your repository

echo "🚀 Setting up Git repository for Review Scraper..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed or not in PATH"
    echo "Please install Git from: https://git-scm.com/download/windows"
    echo "Or use GitHub Desktop: https://desktop.github.com"
    exit 1
fi

# Initialize repository if not already initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Add all files
echo "📄 Adding files to Git..."
git add .

# Check if there are any changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    # Commit files
    echo "💾 Committing files..."
    git commit -m "Initial commit: Review Scraper for Yelp and Amazon

Features:
- Production-ready Flask API
- Yelp and Amazon review scraping
- Comprehensive error handling
- Railway deployment ready
- Real-time data fetching
- Background scraping with intervals"
fi

echo "
🎉 Git repository setup complete!

Next steps:
1. Create a GitHub repository at: https://github.com/new
2. Copy the repository URL
3. Run: git remote add origin <your-repo-url>
4. Run: git branch -M main
5. Run: git push -u origin main

Then deploy to Railway:
1. Go to https://railway.app
2. Click 'Start a New Project'
3. Select 'Deploy from GitHub repo'
4. Choose your repository
5. Deploy automatically!

For detailed instructions, see DEPLOYMENT.md
"
