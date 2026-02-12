# Use slim Python base
FROM python:3.11-slim

# 1. Install System Dependencies efficiently
# We use nodesource to get Node.js without the 600+ debian-native node packages bloat
RUN apt-get update && apt-get install -y curl build-essential git && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
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
# Wildcards prevent build failure if .env.local isn't in Git (Railway ENV vars will take over)
COPY src/.env.loca[l] ./src/
COPY web/.env.loca[l] ./web/

# 7. Build Frontend
WORKDIR /app/web
RUN npm run build

# 8. Final Configuration
EXPOSE 3000 8000 8765

# Start both services in parallel
WORKDIR /app
CMD ["sh", "-c", "python src/agent.py dev & cd web && npm run dev:web"]
