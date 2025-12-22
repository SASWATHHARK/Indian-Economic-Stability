# Deployment Guide

## Prerequisites

- GitHub account
- Render/Railway account (for backend)
- Netlify/Vercel account (for frontend)

## Backend Deployment (Render/Railway)

### Option 1: Render

1. **Create New Web Service:**
   - Go to Render dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Settings:**
   - **Name:** economic-stability-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python backend/main.py`
   - **Root Directory:** (leave empty)

3. **Environment Variables:**
   - `PYTHON_VERSION`: 3.9
   - `API_HOST`: 0.0.0.0
   - `API_PORT`: 8000

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for build to complete
   - Note the service URL (e.g., `https://your-api.onrender.com`)

### Option 2: Railway

1. **Create New Project:**
   - Go to Railway dashboard
   - Click "New Project"
   - Connect GitHub repository

2. **Configure Service:**
   - Railway auto-detects Python
   - Set start command: `python backend/main.py`
   - Add environment variables if needed

3. **Deploy:**
   - Railway auto-deploys on push
   - Get service URL from dashboard

## Frontend Deployment (Netlify/Vercel)

### Option 1: Netlify

1. **Build Locally:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Deploy:**
   - Go to Netlify dashboard
   - Drag and drop `frontend/build` folder
   - Or connect GitHub repository

3. **Configure:**
   - **Build command:** `npm run build`
   - **Publish directory:** `build`
   - **Environment variables:**
     - `REACT_APP_API_URL`: Your backend URL

4. **Deploy:**
   - Netlify auto-deploys on push
   - Get site URL (e.g., `https://your-site.netlify.app`)

### Option 2: Vercel

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   ```bash
   cd frontend
   vercel
   ```

3. **Configure:**
   - Set environment variables in Vercel dashboard
   - `REACT_APP_API_URL`: Your backend URL

## Local Deployment (For Evaluation)

### Step 1: Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r ../requirements.txt
python main.py
```

Backend runs on `http://localhost:8000`

### Step 2: Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

## Environment Configuration

### Backend (.env)
```env
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
# For production: REACT_APP_API_URL=https://your-api.onrender.com
```

## Troubleshooting

### Backend Issues

**Problem:** Module not found
- **Solution:** Ensure all dependencies in `requirements.txt` are installed

**Problem:** Port already in use
- **Solution:** Change port in `main.py` or kill process using port 8000

**Problem:** CORS errors
- **Solution:** Update CORS origins in `main.py` to include frontend URL

### Frontend Issues

**Problem:** API calls failing
- **Solution:** Check `REACT_APP_API_URL` environment variable

**Problem:** Build fails
- **Solution:** Ensure Node.js version is 16+ and all dependencies installed

**Problem:** Charts not rendering
- **Solution:** Check browser console for errors, ensure Recharts is installed

## Production Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend environment variable set
- [ ] CORS configured for production URL
- [ ] API endpoints tested
- [ ] Error handling working
- [ ] Loading states implemented
- [ ] Mobile responsive design tested
- [ ] Documentation updated with production URLs

## Monitoring

### Backend Health Check
```bash
curl https://your-api.onrender.com/health
```

### Frontend
- Check browser console for errors
- Test all pages and features
- Verify API connectivity

## Cost Considerations

### Free Tier Limits:
- **Render:** 750 hours/month (free tier)
- **Railway:** $5 credit/month (free tier)
- **Netlify:** 100GB bandwidth/month (free tier)
- **Vercel:** Unlimited (free tier for personal projects)

### Recommendations:
- Use free tiers for academic projects
- Monitor usage to avoid overages
- Consider local deployment for evaluation

## Security Notes

1. **API Keys:** Never commit API keys to repository
2. **CORS:** Restrict CORS to specific domains in production
3. **HTTPS:** Always use HTTPS in production
4. **Environment Variables:** Use platform's environment variable management

## Backup Strategy

1. **Code:** GitHub repository (already backed up)
2. **Data:** Models can be retrained from fresh data
3. **Configuration:** Document all environment variables

## Rollback Procedure

1. **Backend:** Revert to previous commit in Render/Railway
2. **Frontend:** Revert to previous commit in Netlify/Vercel
3. **Local:** Use git to revert changes

