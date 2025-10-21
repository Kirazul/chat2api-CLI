# Railway Deployment Guide for Chat2API

This guide will help you deploy your Chat2API server to Railway.

## Prerequisites

1. A Railway account (sign up at https://railway.app)
2. Git repository with your code
3. Railway CLI (optional but recommended)

## Deployment Steps

### 1. Prepare Your Repository

The following files have been created for Railway deployment:
- `railway.json` - Railway configuration
- `Procfile` - Process definition
- `runtime.txt` - Python version specification
- `.env.production` - Production environment template

### 2. Deploy to Railway

#### Option A: Deploy via Railway Dashboard (Recommended)

1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select this repository
5. Railway will automatically detect it's a Python project

#### Option B: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 3. Configure Environment Variables

In your Railway project dashboard, go to the "Variables" tab and set:

**Required Variables:**
- `ENVIRONMENT=production`
- `PORT` (Railway sets this automatically)
- `ACTIVE_TOKEN=your_secure_token`

**Optional Variables (customize as needed):**
- `API_PREFIX=your_prefix`
- `AUTHORIZATION=your_auth_tokens`
- `AUTH_KEY=your_auth_key`
- `CHATGPT_BASE_URL=https://chatgpt.com`
- `PROXY_URL=your_proxy_urls`
- `ENABLE_GATEWAY=true`
- `HISTORY_DISABLED=true`
- `POW_DIFFICULTY=000032`
- `RETRY_TIMES=3`

### 4. Domain Configuration

1. Railway will provide a default domain like `your-app-name.up.railway.app`
2. You can add a custom domain in the "Settings" tab
3. Update your `config.json` if needed (it's configured to use Railway's domain automatically)

### 5. Health Checks

The server includes health check endpoints:
- `/health` - Basic health check
- `/` - Root endpoint with version info

Railway will use the `/health` endpoint to monitor your service.

### 6. Logs and Monitoring

- View logs in Railway dashboard under "Deployments"
- Monitor resource usage in the "Metrics" tab
- Set up alerts in "Settings" > "Notifications"

## Important Notes

1. **Security**: Never commit sensitive tokens to your repository. Use Railway's environment variables.
2. **Scaling**: Railway automatically handles scaling based on traffic.
3. **Database**: If you need persistent storage, add a Railway database service.
4. **Custom Domain**: Configure SSL certificates through Railway's dashboard.

## Troubleshooting

### Common Issues:

1. **Build Failures**: Check that all dependencies are in `requirements.txt`
2. **Port Issues**: Ensure your app uses `PORT` environment variable
3. **Environment Variables**: Verify all required variables are set in Railway dashboard

### Useful Commands:

```bash
# View logs
railway logs

# Connect to your deployment
railway shell

# Check service status
railway status
```

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Chat2API Issues: Check your repository's issues page