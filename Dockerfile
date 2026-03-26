# LOOP-DeerFlow Production Dockerfile
# Deploys DeerFlow backend to Fly.io

FROM python:3.12-slim

ARG NODE_MAJOR=22

# Install system dependencies + Node.js
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    gnupg \
    ca-certificates \
    git \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.7.20 /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy entire repo (backend is at root)
COPY . .

# Install dependencies
RUN cd backend && uv sync

# Copy startup script
COPY scripts/start-production.sh ./start.sh
RUN chmod +x start.sh

# Expose gateway port
EXPOSE 8000

# Start command
CMD ["./start.sh"]
