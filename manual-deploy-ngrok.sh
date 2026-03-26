#!/bin/bash
# Manual local deploy with ngrok public URL
# Run this on any machine with Docker

# Build image
docker build -t loop-deerflow .

# Run container
docker run -d \
  --name loop-deerflow \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY=sk-or-v1-... \
  -e E2B_API_KEY=e2b_... \
  loop-deerflow

# Install ngrok (one-time)
# npm install -g ngrok
# OR download from https://ngrok.com/download

# Expose to public internet
ngrok http 8000

# Output will show:
# Forwarding: https://xxxx.ngrok-free.app -> http://localhost:8000
