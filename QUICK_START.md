# Quick Start Guide - Fix "Failed to fetch data" Error

## 🚨 Problem: "Error: Failed to fetch data"

This error means your **backend server is not running**. The frontend (React) cannot connect to the backend (FastAPI).

## ✅ Solution: Start the Backend Server

### Step 1: Open Terminal/Command Prompt

### Step 2: Navigate to Backend Directory
```bash
cd backend
```

### Step 3: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

**You should see `(venv)` in your terminal prompt**

### Step 4: Start Backend Server
```bash
python main.py
```

### Step 5: Wait for Success Message
You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Backend is now running!**

### Step 6: Keep This Terminal Open
**DO NOT CLOSE THIS TERMINAL** - Backend must keep running

### Step 7: Refresh Frontend Browser
Go back to your browser and **refresh the page** (F5)

**The error should be gone! ✅**

---

## 📋 Complete Setup (Both Backend + Frontend)

### Terminal 1 - Backend (Run First):
```bash
cd backend
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux

python main.py
```
**Keep this terminal open!**

### Terminal 2 - Frontend (Run Second):
```bash
cd frontend
npm start
```
**Browser will open automatically**

---

## 🔍 Verify Backend is Running

**Open browser and go to:**
```
http://localhost:8000/health
```

**You should see:**
```json
{"status": "healthy", "timestamp": "..."}
```

**If you see this, backend is working! ✅**

---

## ❌ Still Not Working?

### Check These:

1. **Backend terminal shows errors?**
   - Install dependencies: `pip install -r ../requirements.txt`
   - Check internet connection (needed for Yahoo Finance)

2. **Port 8000 already in use?**
   - Close other applications using port 8000
   - Or change port in `backend/main.py` line 245

3. **Frontend still shows error?**
   - Make sure backend terminal is still running
   - Refresh browser (F5)
   - Check browser console (F12) for detailed errors

4. **Need more help?**
   - See `TROUBLESHOOTING.md` for detailed guide
   - See `docs/SETUP_GUIDE.md` for complete setup

---

## 💡 Important Notes

- **Backend MUST be running** for frontend to work
- Keep backend terminal open while using the app
- Backend runs on port 8000
- Frontend runs on port 3000
- Both must run simultaneously

---

**Quick Fix Summary:**
1. Open terminal
2. `cd backend`
3. `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. `python main.py`
5. Wait for "Uvicorn running" message
6. Refresh browser

**That's it! 🎉**


