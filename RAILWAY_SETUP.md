# 🚀 Railway Deployment Setup

## Quick Fix for Current Error

The error shows Railway is trying to use SQLite instead of PostgreSQL. Here's how to fix it:

### **Step 1: Set Environment Variables in Railway**

1. **Go to your Railway project dashboard**
2. **Click on your service** (the web app, not the database)
3. **Go to "Variables" tab**
4. **Add this environment variable:**

```
DATABASE_URL=postgresql+asyncpg://postgres:jLeJrmbjMdzgDpRFrufSCuwthfEZAxDi@switchback.proxy.rlwy.net:37083/railway
```

### **Step 2: Alternative - Use Railway's Auto-Generated URL**

If Railway provided a different `DATABASE_URL`, use that instead. Railway usually provides a URL like:
```
DATABASE_URL=postgresql://postgres:password@host:port/railway
```

### **Step 3: Redeploy**

After setting the environment variable:
1. Go to your Railway service
2. Click "Deploy" or "Redeploy"
3. Railway will rebuild with the correct database

## Environment Variables for Railway

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Your PostgreSQL connection string |
| `BASE_URL` | `https://your-app.railway.app` | Your app's public URL |
| `PORT` | `8000` | Server port (auto-set by Railway) |

## Troubleshooting

### **If still getting SQLite error:**
1. Check that `DATABASE_URL` is set in Railway dashboard
2. Make sure it starts with `postgresql://` or `postgresql+asyncpg://`
3. Redeploy the service

### **If database connection fails:**
1. Verify the PostgreSQL service is running
2. Check the connection string format
3. Ensure the database is accessible

### **If tables don't exist:**
The release script will create them automatically. If it fails:
1. Check Railway logs for the release phase
2. Manually run the release script if needed

## Expected Railway Logs

You should see:
```
🔗 Railway Release Phase - Creating database tables...
Database URL: postgresql+asyncpg://...
✅ Database tables created successfully
```

## Success Indicators

✅ **Release Phase**: Tables created successfully  
✅ **Web Phase**: Server starts on port 8000  
✅ **Health Check**: `/health` endpoint responds  
✅ **API Docs**: `/docs` accessible  

Your app will be live at: `https://your-app.railway.app`
