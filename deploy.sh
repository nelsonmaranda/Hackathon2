#!/bin/bash

# EduVerse Railway Deployment Script
# This script helps you deploy your application to Railway

echo "🚀 EduVerse Railway Deployment Script"
echo "===================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
else
    echo "✅ Railway CLI is already installed"
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway..."
    railway login
else
    echo "✅ Already logged in to Railway"
fi

# Initialize Railway project if not already done
if [ ! -f ".railway" ]; then
    echo "🚂 Initializing Railway project..."
    railway init
else
    echo "✅ Railway project already initialized"
fi

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "🎉 Deployment completed!"
echo "📱 Your app should now be live on Railway!"
echo "🔗 Check your Railway dashboard for the live URL"
echo ""
echo "📋 Next steps:"
echo "1. Set up your environment variables in Railway dashboard"
echo "2. Configure your MySQL database"
echo "3. Add your Hugging Face API key"
echo "4. Test your application!"
