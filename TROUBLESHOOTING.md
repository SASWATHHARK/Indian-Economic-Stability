# Troubleshooting Guide - "Failed to fetch data" Error

## Common Issue: Frontend Cannot Connect to Backend

If you see "Error: Failed to fetch data" in the frontend, it means the React app cannot connect to the FastAPI backend.

## Quick Fix Checklist

### ✅ Step 1: Check if Backend is Running

**Open a terminal/command prompt and run:**

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Start backend server
python main.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**If you see this, backend is running! ✅**

### ✅ Step 2: Verify Backend is Accessible

**Open your browser and go to:**
```
http://localhost:8000/health
```

**You should see:**
```json
{"status": "healthy", "timestamp": "..."}
```

**If you see this, backend is working! ✅**

### ✅ Step 3: Check Frontend API Configuration

**The frontend is configured to connect to:**
- Default: `http://localhost:8000`
- Or: Value from `REACT_APP_API_URL` environment variable

**To check/change the API URL:**

1. **Check current configuration:**
   - Open `frontend/src/services/api.js`
   - Line 3 shows: `const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';`

2. **If backend runs on different port, create `.env` file:**
   ```bash
   cd frontend
   # Create .env file
   ```
   
   **Add to `.env` file:**
   ```env
   REACT_APP_API_URL=http://localhost:8000
   ```
   
   **Note:** Replace `8000` with your actual backend port if different.

3. **Restart frontend after changing .env:**
   ```bash
   # Stop frontend (Ctrl+C)
   # Then restart
   npm start
   ```

### ✅ Step 4: Check Port Conflicts

**Backend Port 8000 Already in Use?**

**Windows:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill
```

**Or change backend port in `backend/main.py`:**
```python
# Change line 245 from:
uvicorn.run(app, host="0.0.0.0", port=8000)

# To:
uvicorn.run(app, host="0.0.0.0", port=8001)  # Or any available port
```

**Then update frontend `.env`:**
```env
REACT_APP_API_URL=http://localhost:8001
```

### ✅ Step 5: Check CORS Configuration

**If you see CORS errors in browser console:**

1. **Check `backend/main.py` line 26:**
   ```python
   allow_origins=["http://localhost:3000", "http://localhost:5173"]
   ```

2. **If frontend runs on different port, add it:**
   ```python
   allow_origins=[
       "http://localhost:3000", 
       "http://localhost:5173",
       "http://localhost:YOUR_PORT"  # Add your port
   ]
   ```

3. **Restart backend after changes**

## Detailed Error Messages

### Error: "Network Error" or "ECONNREFUSED"
**Meaning:** Backend server is not running or not accessible

**Solution:**
1. Start backend server (Step 1)
2. Verify backend is running (Step 2)
3. Check firewall settings (may block localhost connections)

### Error: "CORS policy" or "CORS error"
**Meaning:** Backend is blocking frontend requests

**Solution:**
1. Check CORS configuration (Step 5)
2. Ensure frontend URL is in `allow_origins` list
3. Restart backend

### Error: "404 Not Found"
**Meaning:** API endpoint doesn't exist

**Solution:**
1. Check backend is running latest code
2. Verify endpoint exists in `backend/main.py`
3. Test endpoint directly: `http://localhost:8000/market-data`

### Error: "500 Internal Server Error"
**Meaning:** Backend has an error

**Solution:**
1. Check backend terminal for error messages
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Check internet connection (needed for Yahoo Finance API)

## Step-by-Step Setup (Complete)

### Terminal 1 - Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux

pip install -r ../requirements.txt
python main.py
```

**Wait for:** `INFO:     Uvicorn running on http://0.0.0.0:8000`

### Terminal 2 - Frontend:
```bash
cd frontend
npm install
npm start
```

**Wait for:** Browser to open at `http://localhost:3000`

## Testing Connection

### Test 1: Backend Health Check
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status": "healthy", ...}`

### Test 2: Backend API
```bash
curl http://localhost:8000/market-data
```
**Expected:** JSON with market data

### Test 3: Frontend Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for errors
4. Go to Network tab
5. Refresh page
6. Check if API calls are made
7. Check response status (should be 200)

## Common Issues and Solutions

### Issue: "Module not found" in backend
**Solution:**
```bash
cd backend
venv\Scripts\activate
pip install -r ../requirements.txt
```

### Issue: "npm not found" in frontend
**Solution:**
- Install Node.js from https://nodejs.org/
- Restart terminal after installation

### Issue: Backend starts but immediately crashes
**Solution:**
1. Check error message in terminal
2. Common causes:
   - Missing dependencies
   - Port already in use
   - Internet connection (for Yahoo Finance)

### Issue: Frontend shows loading forever
**Solution:**
1. Check browser console (F12) for errors
2. Check Network tab for failed requests
3. Verify backend is running
4. Check API URL configuration

## Still Not Working?

### Debug Steps:

1. **Check Backend Logs:**
   - Look at terminal where backend is running
   - Check for error messages
   - Note any stack traces

2. **Check Frontend Console:**
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Check Network tab for API calls

3. **Test Backend Directly:**
   - Open: `http://localhost:8000/health`
   - Open: `http://localhost:8000/market-data`
   - If these don't work, backend has issues

4. **Check Firewall/Antivirus:**
   - May block localhost connections
   - Temporarily disable to test

5. **Restart Everything:**
   - Stop both backend and frontend
   - Close all terminals
   - Start fresh

## Quick Test Script

**Create `test_backend.py` in project root:**
```python
import requests

try:
    response = requests.get('http://localhost:8000/health')
    print("✅ Backend is running!")
    print(f"Response: {response.json()}")
except requests.exceptions.ConnectionError:
    print("❌ Backend is NOT running!")
    print("Please start backend: cd backend && python main.py")
except Exception as e:
    print(f"❌ Error: {e}")
```

**Run:**
```bash
python test_backend.py
```

## Need More Help?

1. Check `docs/SETUP_GUIDE.md` for detailed setup
2. Review error messages carefully
3. Check browser console for detailed errors
4. Verify all steps in this guide

---

**Remember:** Both backend AND frontend must be running simultaneously!


