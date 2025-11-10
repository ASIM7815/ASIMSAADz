# 🚀 Quick Deploy to Render

## Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Ready for Render deployment"
git remote add origin https://github.com/YOUR_USERNAME/ai-code-analyzer.git
git push -u origin main
```

## Step 2: Deploy on Render
1. Go to [render.com](https://render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repo
4. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cc`
   - **Instance Type**: Free

## Step 3: Done! 🎉
Your app will be live at: `https://your-app-name.onrender.com`

---

## Files Ready for Deployment ✅

- ✅ `requirements.txt` - Updated with gunicorn
- ✅ `render.yaml` - Auto-deployment config
- ✅ `app.py` - Production-ready with PORT handling
- ✅ `.gitignore` - Excludes sensitive files

---

**Full guide**: See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
