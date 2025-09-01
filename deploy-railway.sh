#!/bin/bash

echo "========================================"
echo "    EduVerse Railway Deployment"
echo "========================================"
echo

echo "Installing Railway CLI..."
npm install -g @railway/cli

echo
echo "Please login to Railway..."
railway login

echo
echo "Linking to Railway project..."
railway link

echo
echo "Deploying to Railway..."
railway up

echo
echo "Deployment complete! Check your Railway dashboard."
