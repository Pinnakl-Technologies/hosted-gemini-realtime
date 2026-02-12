# Use slim Python base (v3.11)
FROM python:3.11-slim

# 1. Install Node.js & System Deps efficiently
# Using NodeSource reduces build bloat from ~1GB to ~100MB
RUN apt-get update && apt-get install -y curl build-essential git && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g concurrently && \
    rm -rf /var/lib/apt/lists/*

# 2. Set Working Directory
WORKDIR /app

# 3. Setup Python Backend (Metadata first for caching)
COPY src/requirements.txt ./src/
RUN pip install --upgrade pip && \
    pip install -r src/requirements.txt

# 4. Setup Frontend (Metadata first for caching)
COPY web/package*.json ./web/
WORKDIR /app/web
RUN npm install

# 5. Copy Application Source
WORKDIR /app
COPY src ./src
COPY web ./web

# 6. Sync Environment Files (Robust Copy)
# Using wildcards [l] avoids build failure if the local .env.local isn't pushed to Git.
# This allows the container to fall back to Railway's "Variables" tab.
COPY src/.env.loca[l] ./src/
COPY web/.env.loca[l] ./web/

# 7. Build Frontend (Production Ready)
WORKDIR /app/web
RUN npm run build

# 8. Final Configuration
# Expose Next.js and LiveKit Agent ports
EXPOSE 3000 8000 8765

# Start both services in parallel
WORKDIR /app
CMD ["concurrently", "\"python src/agent.py start\"", "\"cd web && npm start\""]
