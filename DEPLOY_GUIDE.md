# Deployment Guide - Rytech Flask App to Render

## ✅ STEP 1: Verify All Files Exist

Run this in terminal to check all required files are present:

```bash
ls -la app.py requirements.txt Dockerfile render.yaml .env.example static/ templates/
```

Expected files:
- ✅ `app.py` (main Flask app)
- ✅ `requirements.txt` (dependencies)
- ✅ `Dockerfile` (Python 3.11 container)
- ✅ `render.yaml` (Render config - Docker mode)
- ✅ `static/` folder (CSS, JS)
- ✅ `templates/` folder (HTML templates)
- ✅ `.env.example` (environment template)

---

## ✅ STEP 2: Verify Git is Set Up

```bash
git status
```

Should show:
- All files committed (clean working directory)
- On `main` branch

If not, commit everything:
```bash
git add .
git commit -m "final deployment ready"
git push
```

Check: Go to your GitHub repo - should see all files there

---

## ✅ STEP 3: Test App Locally (Optional but Recommended)

```bash
python app.py
```

You should see:
```
WARNING in app.run():
   * Running on http://127.0.0.1:5000
```

Visit: http://localhost:5000

Expected: Login page or welcome page loads

Press `Ctrl+C` to stop

---

## 🚀 STEP 4: Deploy to Render (Web Service Setup)

### 4.1 - Go to Render Dashboard

1. Open https://dashboard.render.com
2. Sign in with your GitHub account
3. Click **"New +"** button → Select **"Web Service"**

### 4.2 - Connect GitHub Repository

1. Click **"Connect repository"**
2. Search for: `Rytech` (your repo name)
3. Click **"Connect"**
4. Authorizations: Click **"Authorize render"** if prompted

### 4.3 - Configure Web Service

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `rytech` |
| **Environment** | `Docker` ← **IMPORTANT!** |
| **Branch** | `main` |
| **Dockerfile path** | `Dockerfile` (leave default) |
| **Docker Command** | (leave empty) |

### 4.4 - Instance Type & Plan

- **Instance Type**: `Free`
- **Auto-deploy**: Toggle ON (auto-redeploy on GitHub push)

### 4.5 - Environment Variables

Click **"Add Environment Variable"** and add:

```
MONGODB_URI=your_mongodb_connection_string_here
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=your_secret_key_here
```

**Where to get these?**
- `MONGODB_URI`: Get from MongoDB Atlas connection string
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: Get from Google Cloud Console OAuth credentials
- `SECRET_KEY`: Generate random string (Flask session key)

### 4.6 - Deploy

Click **"Deploy"** button

You'll see logs showing:
```
==> Building Docker image...
==> Running 'pip install -r requirements.txt'...
==> Build successful 🎉
==> Deploying...
==> Running gunicorn...
```

---

## ✅ STEP 5: Monitor Deployment

### During Deploy (5-10 minutes):

Watch the logs in Render dashboard:
- ✅ Docker image builds
- ✅ Python 3.11 uses for build (check logs for `Python-3.11`)
- ✅ Dependencies install (numpy, scikit-learn, Flask, etc.)
- ✅ Build completes successfully

### Common Issues:

| Issue | Solution |
|-------|----------|
| `Environment not Docker` | Go to Settings → Change from Python to Docker → Save → Redeploy |
| `pkg_resources error` | This means Python 3.14 is running. Change to Docker (Step 4.3) |
| `ModuleNotFoundError pandas` | This is OK - pandas is not in requirements.txt (only for training) |
| `Build fails - setuptools` | Already pinned in requirements.txt - should work |

---

## ✅ STEP 6: Test Live App

Once deployment succeeds:

1. Go to Render dashboard → rytech service
2. Copy the **URL** (looks like: `https://rytech-xxxx.onrender.com`)
3. Open in browser: `https://rytech-xxxx.onrender.com`

**Expected:**
- ✅ Login page loads
- ✅ No error 500
- ✅ Google OAuth button appears

**Test features:**
- Try to login with Google
- Submit crop prediction
- Check if results display

---

## 📝 STEP 7: Environment Variables Setup

If not already done in Step 4.5:

### MongoDB Setup:

1. Go to https://www.mongodb.com/cloud/atlas
2. Create account and database cluster
3. Click **"Connect"** → Choose **"Drivers"** → Copy connection string
4. Replace `<username>` and `<password>` with your credentials
5. Add to Render as `MONGODB_URI`

### Google OAuth Setup:

1. Go to https://console.cloud.google.com
2. Create new project: `Rytech`
3. Go to **APIs & Services** → **Credentials**
4. Click **"Create Credentials"** → **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Authorized JavaScript origins: Add your Render URL
7. Authorized redirect URIs: Add `https://your-render-url/auth/google/callback`
8. Copy Client ID and Client Secret → Add to Render

### Secret Key Setup:

Generate random key:
```python
import secrets
print(secrets.token_hex(32))
```

Add output to Render as `SECRET_KEY`

---

## ✅ STEP 8: Auto-Deploy on GitHub Push

Once deployed:

1. Make changes to your code locally
2. Commit and push:
   ```bash
   git add .
   git commit -m "your message"
   git push
   ```
3. Render automatically redeploys (watch logs in dashboard)
4. New version live in 5-10 minutes

---

## 🎉 SUCCESS CHECKLIST

- [ ] Docker image built successfully (logs show Python 3.11)
- [ ] All dependencies installed (numpy, scikit-learn, Flask, etc.)
- [ ] App starts without errors (gunicorn running on port)
- [ ] Website loads in browser
- [ ] Login button appears
- [ ] Can submit predictions
- [ ] Results display correctly

---

## ⚠️ If Deployment Fails

### Check these in order:

1. **Service Type is Docker?**
   - Render dashboard → Settings → Environment should be "Docker"
   - NOT "Python"

2. **Logs show Python 3.14?**
   - Change to Docker (above)

3. **pkg_resources error?**
   - Means Python 3.14 is running
   - Change to Docker and redeploy

4. **scikit-learn compilation error?**
   - Already removed pandas from requirements.txt
   - Should not happen with Python 3.11

5. **Port binding error?**
   - Dockerfile and render.yaml already configured correctly
   - Should auto-bind to Render's PORT env var

---

## 📞 Troubleshooting Commands

### View logs locally:
```bash
python app.py
# Press Ctrl+C to stop
```

### Check dependencies installed:
```bash
pip list | grep -E "Flask|scikit-learn|pymongo|authlib"
```

### Test specific imports:
```bash
python -c "import flask; import sklearn; import pymongo; print('All good!')"
```

### View Render logs:
- Go to Render dashboard
- Click on "rytech" service
- Click "Logs" tab
- Watch in real-time as app deploys

---

## 🎯 Quick Deploy Summary

1. ✅ All files ready (checked in Step 1)
2. ✅ Git repo on GitHub (checked in Step 2)
3. 🚀 Open https://dashboard.render.com → New Web Service → Connect GitHub
4. 🚀 Set Environment = "Docker"
5. 🚀 Add environment variables (MongoDB, Google OAuth, Secret Key)
6. 🚀 Click Deploy
7. ✅ Wait 5-10 minutes
8. ✅ Test live URL
9. 🎉 Done!

