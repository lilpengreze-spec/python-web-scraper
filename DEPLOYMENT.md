# Railway Deployment Guide

This guide will help you deploy your Review Scraper to Railway.

## 🚀 Option 1: Deploy via GitHub (Recommended)

### Prerequisites
- Git installed on your machine
- GitHub account
- Railway account (sign up at [railway.app](https://railway.app))

### Steps

1. **Install Git** (if not already installed)
   - Download from [git-scm.com](https://git-scm.com/download/windows)
   - Or use GitHub Desktop: [desktop.github.com](https://desktop.github.com)

2. **Initialize Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Review Scraper for Yelp and Amazon"
   ```

3. **Create GitHub Repository**
   - Go to [github.com](https://github.com) and create a new repository
   - Name it something like "review-scraper" or "yelp-amazon-scraper"
   - Don't initialize with README (since we already have one)

4. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

5. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect it's a Python project and deploy

6. **Set Environment Variables** (Optional)
   - In Railway dashboard, go to your project
   - Click on "Variables"
   - Add these variables if you have API keys:
     ```
     YELP_API_KEY=your_yelp_api_key
     AMAZON_ACCESS_KEY=your_amazon_access_key
     AMAZON_SECRET_KEY=your_amazon_secret_key
     AMAZON_PARTNER_TAG=your_amazon_partner_tag
     ```

## 🎯 Option 2: Direct Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Deploy from current directory**
   ```bash
   railway deploy
   ```

## 🎮 Option 3: Direct Upload (No Git)

1. **Create a ZIP file** of your project folder
2. **Go to Railway dashboard**
3. **Select "Deploy from ZIP"**
4. **Upload your ZIP file**

## ✅ Verification

After deployment, Railway will provide you with a URL like:
`https://your-app-name.up.railway.app`

Test these endpoints:
- `GET /health` - Should return health status
- `POST /scrape` - Test with sample data
- `GET /latest` - Get latest scraped data

## 🔧 Configuration Files Already Included

Your project includes these Railway-ready files:
- ✅ `Procfile` - Tells Railway how to run your app
- ✅ `railway.json` - Railway build configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `.gitignore` - Git ignore rules
- ✅ `app.json` - App configuration

## 🐛 Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check that `requirements.txt` includes all dependencies
   - Ensure Python version compatibility

2. **App Won't Start**
   - Verify `Procfile` contains: `web: gunicorn app:app`
   - Check Railway logs for error messages

3. **Environment Variables**
   - API keys are optional - app will work with web scraping only
   - Set `FLASK_ENV=production` for production deployment

### Logs and Debugging:
- View logs in Railway dashboard
- Use the "Logs" tab to see real-time output
- Check for any error messages during deployment

## 🎉 Success!

Once deployed successfully, your Review Scraper will be available at:
- Health check: `https://your-app.railway.app/health`
- API documentation: See README.md for endpoint details

## 💡 Next Steps

1. **Test your API** with the provided endpoints
2. **Monitor usage** in Railway dashboard
3. **Scale as needed** using Railway's scaling options
4. **Add custom domain** if desired (Railway Pro feature)

---

Need help? Check the Railway documentation or open an issue in your repository!
