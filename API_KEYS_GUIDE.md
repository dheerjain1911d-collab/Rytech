# Complete API Keys & Credentials Guide

This guide explains how to get EVERY credential needed for your Render deployment.

---

## 📋 Credentials You Need

1. **MONGODB_URI** - Database connection string
2. **GOOGLE_CLIENT_ID** - Google OAuth app ID
3. **GOOGLE_CLIENT_SECRET** - Google OAuth app secret
4. **SECRET_KEY** - Flask session encryption key

---

# 1️⃣ MONGODB_URI (Database Connection)

## Step 1.1: Create MongoDB Account

1. Go to: https://www.mongodb.com/cloud/atlas
2. Click **"Try Free"** button (top right)
3. Choose: **"Sign up with Email"**
4. Fill in:
   - Email address
   - Password
   - First name & Last name
5. Accept terms and click **"Create account"**
6. Check your email - MongoDB will send verification link
7. Click the verification link in email

---

## Step 1.2: Create Free Database Cluster

After email verification, you'll see MongoDB Atlas dashboard:

1. Click **"Build a Database"** (large button in center)
2. Choose **"Free"** option (M0 - free tier)
3. Click **"Create"**
4. Select:
   - **Cloud Provider**: AWS (default)
   - **Region**: Choose closest to you (e.g., `us-east-1` for USA)
5. Click **"Create Cluster"**

**Wait 2-3 minutes** for cluster to be created (shows "Provisioning" status)

---

## Step 1.3: Create Database User

When cluster is ready, you'll see security prompt:

1. Click **"Security Quickstart"** (or go to Security tab)
2. Click **"Create a Database User"**
3. Fill in:
   - **Username**: `rytech` (any name you want)
   - **Password**: Generate or create strong password (SAVE THIS!)
   - Click **"Autogenerate Secure Password"** for strong random password
4. Click **"Create User"**

**IMPORTANT**: Save your username and password somewhere safe!

---

## Step 1.4: Allow Network Access

1. Still in Security tab, click **"Network Access"**
2. Click **"Add IP Address"** button
3. Click **"Allow Access from Anywhere"** (for free tier)
4. Click **"Confirm"**

This allows Render to connect to your database from anywhere.

---

## Step 1.5: Get Connection String

1. Go back to **"Databases"** tab (main cluster view)
2. Click **"Connect"** button (large button on your cluster)
3. Choose **"Drivers"** option
4. Select:
   - **Driver**: Python
   - **Version**: 4.0 or later
5. You'll see a connection string like:

```
mongodb+srv://rytech:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

6. **Replace `<password>` with your actual password** you created in Step 1.3

**Example:**
```
mongodb+srv://rytech:MyPassword123@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
```

7. **Copy this entire string** - this is your `MONGODB_URI`

---

# 2️⃣ GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET (OAuth Login)

## Step 2.1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com
2. If you don't have a Google account, create one: https://accounts.google.com/signup
3. After login, at top, click **"Select a Project"** dropdown
4. Click **"New Project"**
5. Fill in:
   - **Project name**: `Rytech` (or any name)
   - Leave Organization blank
6. Click **"Create"**

**Wait 1-2 minutes** for project creation

---

## Step 2.2: Enable Google+ API

1. In Google Cloud Console, search for **"Google+ API"** (search bar at top)
2. Click the **"Google+ API"** result
3. Click **"Enable"** button (blue button)

**Wait 30 seconds** for API to enable

---

## Step 2.3: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** (left sidebar)
2. Click **"Credentials"** (left sidebar)
3. Click **"+ Create Credentials"** button (top)
4. Choose **"OAuth 2.0 Client ID"**
5. You'll see a warning: **"Configure OAuth Consent Screen First"**
6. Click **"Configure Consent Screen"**

---

## Step 2.4: Configure OAuth Consent Screen

1. Choose **"External"** (unless you have Google Workspace)
2. Click **"Create"**
3. Fill in the form:
   - **App name**: `Rytech`
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Click **"Save & Continue"**

**Scopes page:**
- Click **"Add or Remove Scopes"**
- Search for and select:
  - `email`
  - `profile`
  - `openid`
- Click **"Update"**
- Click **"Save & Continue"**

**Summary page:**
- Click **"Save & Continue"**

---

## Step 2.5: Create OAuth Client ID

Now back to create credentials:

1. Go to **"APIs & Services"** → **"Credentials"** (left sidebar)
2. Click **"+ Create Credentials"** → **"OAuth 2.0 Client ID"**
3. Choose **"Web application"** from dropdown
4. Fill in:
   - **Name**: `Rytech Web Client`
   - **Authorized JavaScript origins**: Add your Render URL:
     ```
     https://your-render-url.onrender.com
     https://localhost:5000
     ```
     (Replace `your-render-url` with actual Render URL)
   
   - **Authorized redirect URIs**: Add callback URLs:
     ```
     https://your-render-url.onrender.com/auth/google/callback
     http://localhost:5000/auth/google/callback
     ```

5. Click **"Create"**

---

## Step 2.6: Get Client ID & Secret

After clicking "Create", you'll see a popup showing:

- **Client ID** (long string like: `123456789-abc...xyz.apps.googleusercontent.com`)
- **Client Secret** (long string like: `GOCSP...xyz`)

**Copy both!** These are your:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

**Or download as JSON:**
1. Click **"Download"** to download credentials file
2. Open the JSON file
3. Find `"client_id"` and `"client_secret"`

---

# 3️⃣ SECRET_KEY (Flask Session Key)

This is for Flask to encrypt session cookies. You can generate it easily.

## Step 3.1: Generate Random Secret Key

**On your computer, open terminal and run:**

**On Windows (PowerShell):**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

**On Mac/Linux (Bash):**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Output:**
```
a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6
```

**Copy this entire string** - this is your `SECRET_KEY`

---

## ✅ Summary: Your 4 Credentials

Now you should have all 4:

| Name | Example | Where You Got It |
|------|---------|------------------|
| `MONGODB_URI` | `mongodb+srv://rytech:pass@cluster...` | MongoDB Atlas |
| `GOOGLE_CLIENT_ID` | `123456789-abc...xyz.apps.googleusercontent.com` | Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | `GOCSP...xyz` | Google Cloud Console |
| `SECRET_KEY` | `a1b2c3d4e5f6a1b2...` | Generated with Python |

---

# 🚀 Add Credentials to Render

## Step 1: Go to Render Dashboard

https://dashboard.render.com

---

## Step 2: Navigate to Environment Variables

1. Click on your **"rytech"** service (web service)
2. Click **"Settings"** tab (top)
3. Scroll down to **"Environment Variables"** section

---

## Step 3: Add Each Variable

Click **"Add Environment Variable"** button and fill in:

### First Variable - MongoDB URI

- **Key**: `MONGODB_URI`
- **Value**: `mongodb+srv://rytech:password@cluster...`
- Click **"Save"**

### Second Variable - Google Client ID

- **Key**: `GOOGLE_CLIENT_ID`
- **Value**: `123456789-abc...xyz.apps.googleusercontent.com`
- Click **"Save"**

### Third Variable - Google Client Secret

- **Key**: `GOOGLE_CLIENT_SECRET`
- **Value**: `GOCSP...xyz`
- Click **"Save"**

### Fourth Variable - Secret Key

- **Key**: `SECRET_KEY`
- **Value**: `a1b2c3d4e5f6a1b2...`
- Click **"Save"**

---

## Step 4: Deploy

After adding all 4 variables:

1. Go back to top of Render dashboard
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
   
**OR**

Just push a new commit to GitHub:
```bash
git add .
git commit -m "deployment ready"
git push
```

Render will auto-deploy with the new environment variables.

---

# 🧪 Test Credentials (Optional)

## Test MongoDB Connection

Create a test file `test_mongo.py`:

```python
import pymongo
from pymongo import MongoClient

MONGODB_URI = "YOUR_MONGODB_URI_HERE"

try:
    client = MongoClient(MONGODB_URI)
    db = client.test
    print("✅ MongoDB connected successfully!")
    print(f"Database: {db}")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
```

Run:
```bash
python test_mongo.py
```

---

## Test Google OAuth Setup

In `app.py`, you should see something like:

```python
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
```

Just make sure these environment variables are set in Render, and your app will automatically use them.

---

# ⚠️ Troubleshooting

## "MONGODB_URI not connecting"

**Possible reasons:**
1. Wrong password in connection string
2. Network access not allowed (check MongoDB Atlas → Security → Network Access)
3. Typo in connection string

**Fix:**
1. Go back to MongoDB Atlas
2. Click "Connect" 
3. Copy connection string again
4. Make sure to replace `<password>` with actual password
5. Update in Render environment variables

---

## "Google OAuth not working"

**Possible reasons:**
1. Redirect URI mismatch (must match exactly including https)
2. Client ID or Secret incorrect
3. Google+ API not enabled

**Fix:**
1. Double-check redirect URIs in Google Cloud Console match Render URL exactly
2. Copy-paste Client ID and Secret again (no typos)
3. Make sure Google+ API is enabled in Google Cloud Console

---

## "App crashes on startup"

**Could be missing any of these:**
- `MONGODB_URI` not set
- `GOOGLE_CLIENT_ID` not set
- `GOOGLE_CLIENT_SECRET` not set
- `SECRET_KEY` not set

**Fix:**
1. Go to Render dashboard → your service
2. Click "Settings"
3. Verify all 4 environment variables are there
4. Make sure values are not empty or typos
5. Click "Manual Deploy" to restart with new variables

---

# 📝 Quick Checklist

- [ ] MongoDB Atlas account created
- [ ] Database cluster created (free tier)
- [ ] Database user created (username + password saved)
- [ ] Network access allowed
- [ ] MONGODB_URI copied and saved
- [ ] Google Cloud account created
- [ ] Google+ API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth 2.0 Client ID created
- [ ] GOOGLE_CLIENT_ID copied and saved
- [ ] GOOGLE_CLIENT_SECRET copied and saved
- [ ] SECRET_KEY generated
- [ ] All 4 variables added to Render
- [ ] App deployed successfully

---

**Next Step:** Add all 4 environment variables to Render and deploy! 🚀

