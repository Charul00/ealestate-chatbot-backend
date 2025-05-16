# Render Deployment Guide

## Required Environment Variables

Set these environment variables in your Render dashboard:

1. `SECRET_KEY` - A Django secret key for security
2. `DEBUG` - Set to 'False' for production
3. `RENDER` - Set to 'True' to indicate Render deployment
4. `ALLOWED_HOSTS` - Add your Render domain, e.g., 'realestate-chatbot-api.onrender.com'
5. `OPENAI_API_KEY` - Your OpenAI API key for chat completions (if using OpenAI)

## Build and Start Commands

- **Build Command**: `./build.sh`
- **Start Command**: `./run.sh`

## Deployment Troubleshooting

1. If the application still fails to load despite adding all dependencies:
   - Check Render logs for specific errors
   - You may need to increase plan resources if dealing with memory limits
   - For the free tier, some operations may be limited due to memory constraints

2. If database migrations fail:
   - Run migrations manually via the Render shell

3. If OpenAI integration fails:
   - The application should fall back to demo mode automatically

## Connecting Frontend

Update your frontend to use the deployed API URL:
```javascript
const API_URL = 'https://realestate-chatbot-api.onrender.com/api/query/';
const UPLOAD_URL = 'https://realestate-chatbot-api.onrender.com/api/upload/';
```
