#!/bin/bash
# Quick deploy to Railway using their CLI
# Railway offers $5 free credit, no credit card required

echo "Installing Railway CLI..."
npm install -g @railway/cli

echo "Authenticating..."
export RAILWAY_TOKEN="6ca19fce-820c-49ba-b488-ab11a3e385b1"
railway login --token "$RAILWAY_TOKEN"

echo "Creating project..."
cd ~/loop-deerflow
railway init --name loop-deerflow

echo "Adding PostgreSQL..."
railway add --database postgres

echo "Adding Redis..."
railway add --database redis

echo "Setting environment variables..."
railway variables set DEERFLOW_ENV=production
railway variables set OPENROUTER_API_KEY="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"
railway variables set E2B_API_KEY="e2b_3d2db3fac2ca3cfd538afed8d804f8c77b6fd787"

echo "Deploying..."
railway up

echo "Getting public URL..."
railway domain
