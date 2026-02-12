# Use slim Python base (v3.11)
FROM python:3.11-slim

# 1. Install System Dependencies (Node.js, npm, and build tools)
RUN apt-get update && \
    apt-get install -y nodejs npm curl build-essential git && \
    rm -rf /var/lib/apt/lists/*

# 2. Set Working Directory
WORKDIR /app

# 3. Setup Python Backend
# Copy metadata first for caching
COPY pyproject.toml src/requirements.txt ./src/
RUN pip install --upgrade pip

# 4. Copy Application Source
COPY src ./src
COPY web ./web

# 5. Sync Environment Files
# Ensuring both frontend and backend pick up their respective local configs
COPY src/.env.local ./src/.env.local
COPY web/.env.local ./web/.env.local

# 6. Build Frontend (Next.js)
WORKDIR /app/web
RUN npm install && npm run build

# 7. Final Configuration
# Expose Next.js default port and agent ports
EXPOSE 3000 8000 8765

# Start both services in parallel
# Backend: src/agent.py dev
# Frontend: web/ (next dev)
WORKDIR /app
CMD ["sh", "-c", "python src/agent.py dev & cd web && npm run dev:web"]
