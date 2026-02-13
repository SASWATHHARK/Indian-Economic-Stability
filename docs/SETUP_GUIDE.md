# Complete Setup Guide

## Quick Start (5 Minutes)

### Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.9 or higher installed
- ✅ Node.js 16 or higher installed
- ✅ npm or yarn package manager
- ✅ Internet connection (for data fetching)
- ✅ 16GB RAM recommended (8GB minimum)
- ✅ 2GB free disk space

### Step 1: Clone/Download Project

```bash
# If using git
git clone <repository-url>
cd Indian_Economic_Stability_Project

# Or extract downloaded ZIP file
```

### Step 2: Backend Setup (2 minutes)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Run backend server
python main.py
```

✅ Backend should be running at `http://localhost:8000`

### Step 3: Frontend Setup (2 minutes)

Open a **new terminal window** (keep backend running):

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

✅ Frontend should open at `http://localhost:3000`

### Step 4: Verify Installation

1. Open browser: `http://localhost:3000`
2. You should see the Dashboard
3. Check that data loads (may take a few seconds)

---

## Detailed Setup Instructions

### Backend Setup (Detailed)

#### 1. Python Environment

**Check Python Version:**
```bash
python --version
# Should show Python 3.9 or higher
```

**If Python not installed:**
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

#### 2. Virtual Environment

**Why Virtual Environment?**
- Isolates project dependencies
- Prevents conflicts with other projects
- Best practice for Python projects

**Create Virtual Environment:**
```bash
cd backend
python -m venv venv
```

**Activate Virtual Environment:**

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Verify Activation:**
- You should see `(venv)` in your terminal prompt

#### 3. Install Dependencies

```bash
# Make sure you're in the project root
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

**If Installation Fails:**

**Problem: Microsoft Visual C++ Required (Windows)**
- Solution: Install "Microsoft C++ Build Tools"
- Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/

**Problem: Prophet Installation Fails**
- Solution: Install dependencies separately:
```bash
pip install pystan
pip install prophet
```

**Problem: Permission Denied**
- Solution: Use `pip install --user -r requirements.txt`

#### 4. Run Backend

```bash
python main.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test Backend:**
- Open browser: `http://localhost:8000`
- You should see API information
- Test health: `http://localhost:8000/health`

**Common Issues:**

**Port 8000 Already in Use:**
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill
```

**Module Not Found Error:**
- Solution: Ensure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

### Frontend Setup (Detailed)

#### 1. Node.js Installation

**Check Node.js Version:**
```bash
node --version
# Should show v16 or higher
```

**If Node.js not installed:**
- Download from: https://nodejs.org/
- Install LTS version
- Restart terminal after installation

#### 2. Install Dependencies

```bash
cd frontend
npm install
```

**Expected Output:**
```
added 1234 packages in 2m
```

**If Installation Fails:**

**Problem: npm not found**
- Solution: Reinstall Node.js with npm

**Problem: Permission Denied**
- Solution: Use `npm install --legacy-peer-deps`

**Problem: Network Timeout**
- Solution: Use different registry:
```bash
npm install --registry https://registry.npmjs.org/
```

#### 3. Configure API URL (Optional)

Create `.env` file in `frontend/` directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

**For Production:**
```env
REACT_APP_API_URL=https://your-api.onrender.com
```

#### 4. Start Frontend

```bash
npm start
```

**Expected Output:**
```
Compiled successfully!
You can now view economic-stability-frontend in the browser.
  Local:            http://localhost:3000
```

**Common Issues:**

**Port 3000 Already in Use:**
- Solution: React will ask to use different port (press Y)
- Or kill process using port 3000

**Compilation Errors:**
- Solution: Delete `node_modules` and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

---

## Verification Checklist

### Backend Verification

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] Backend runs without errors
- [ ] API accessible at `http://localhost:8000`
- [ ] Health check returns success

### Frontend Verification

- [ ] Node.js 16+ installed
- [ ] All npm packages installed
- [ ] Frontend runs without errors
- [ ] Browser opens automatically
- [ ] Dashboard loads
- [ ] API calls work (check browser console)

### Integration Verification

- [ ] Dashboard shows stability score
- [ ] Forecast page displays chart
- [ ] Sentiment page shows articles
- [ ] About page loads
- [ ] No console errors

---

## Troubleshooting

### Backend Issues

**Problem: `ModuleNotFoundError: No module named 'fastapi'`**

**Solution:**
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

**Problem: `yfinance` connection error**

**Solution:**
- Check internet connection
- Yahoo Finance may be temporarily unavailable
- Wait a few minutes and retry

**Problem: Prophet model training fails**

**Solution:**
- Ensure sufficient historical data (3 months minimum)
- Check internet connection for data fetching
- Verify yfinance is working

### Frontend Issues

**Problem: `Cannot find module 'react'`**

**Solution:**
```bash
cd frontend
rm -rf node_modules
npm install
```

**Problem: API calls failing (CORS error)**

**Solution:**
- Ensure backend is running
- Check `REACT_APP_API_URL` in `.env`
- Verify CORS settings in `backend/main.py`

**Problem: Charts not rendering**

**Solution:**
- Check browser console for errors
- Ensure Recharts is installed: `npm install recharts`
- Clear browser cache

### General Issues

**Problem: Slow performance**

**Solution:**
- Close other applications
- Ensure sufficient RAM (8GB+)
- Check internet connection speed

**Problem: Data not loading**

**Solution:**
- Check internet connection
- Verify backend is running
- Check browser console for errors
- Wait a few seconds (data fetching takes time)

---

## Development Mode

### Running Both Servers

**Terminal 1 (Backend):**
```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate
python main.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

### Hot Reload

- **Backend:** Restart manually (Ctrl+C, then `python main.py`)
- **Frontend:** Auto-reloads on file changes

### Debugging

**Backend:**
- Check terminal output for errors
- Use `print()` statements
- Check FastAPI docs: `http://localhost:8000/docs`

**Frontend:**
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls

---

## Production Build

### Build Frontend

```bash
cd frontend
npm run build
```

Output: `frontend/build/` directory

### Deploy Backend

See `docs/DEPLOYMENT.md` for detailed deployment instructions.

---

## System Requirements

### Minimum Requirements

- **OS:** Windows 10, macOS 10.14+, or Linux
- **RAM:** 8GB (16GB recommended)
- **Storage:** 2GB free space
- **Internet:** Required for data fetching
- **Python:** 3.9+
- **Node.js:** 16+

### Recommended Requirements

- **RAM:** 16GB
- **CPU:** Multi-core processor
- **Internet:** Stable broadband connection
- **Browser:** Chrome, Firefox, or Edge (latest versions)

---

## Getting Help

### Common Resources

1. **Project README:** `README.md`
2. **API Documentation:** `http://localhost:8000/docs` (when backend running)
3. **React Docs:** https://react.dev/
4. **FastAPI Docs:** https://fastapi.tiangolo.com/

### Error Messages

If you encounter errors:
1. Read the error message carefully
2. Check this guide's troubleshooting section
3. Search error message online
4. Check project issues (if using GitHub)

---

## Next Steps

After successful setup:

1. ✅ Explore the Dashboard
2. ✅ Check Forecast page
3. ✅ Review Sentiment analysis
4. ✅ Read About page for methodology
5. ✅ Review code structure
6. ✅ Prepare for viva presentation

---

**Setup Complete! 🎉**

Your project is now ready for development and demonstration.



