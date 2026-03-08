# Railway Environment Variables Setup Guide

## Required Environment Variables for Railway Deployment

Copy these to Railway Dashboard: **Settings → Variables**

### Django Core Settings
```
SECRET_KEY=your-very-long-random-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=*.up.railway.app,*.railway.app
```

### Database Configuration
Railway PostgreSQL will automatically set `DATABASE_URL`.
But if you need manual config:
```
DB_NAME=${{PGDATABASE}}
DB_USER=${{PGUSER}}
DB_PASSWORD=${{PGPASSWORD}}
DB_HOST=${{PGHOST}}
DB_PORT=${{PGPORT}}
```

### CORS Settings
```
CORS_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:3000
```

## Steps to Deploy:

1. **Create New Project in Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `SmartNeighbour-API`

2. **Add PostgreSQL Database**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will auto-connect to your service

3. **Set Environment Variables**
   - Go to your service → Settings → Variables
   - Add all variables above
   - Generate SECRET_KEY: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

4. **Deploy!**
   - Railway will auto-deploy
   - Check logs for any issues
   - Get your backend URL: `https://your-service.up.railway.app`

5. **Update Frontend**
   - Update Vercel environment variable `NEXT_PUBLIC_API_URL` dengan Railway backend URL
