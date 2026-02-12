# Use Node.js 20 as the base image
FROM node:20-slim

# Install system dependencies and Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Backend Install (Python)
COPY pyproject.toml ./
RUN pip3 install --upgrade pip
RUN pip3 install .

# 2. Frontend Build (Next.js)
WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build

# 3. Final Prep
WORKDIR /app
COPY . .

# Exposure
EXPOSE 3000

# Start both backend agent and frontend web using concurrently
# This keeps both services running in one robust build as requested
CMD ["npx", "concurrently", "-n", "agent,web", "-c", "cyan,magenta", \
    "python src/agent.py start", \
    "npm --prefix web start -- --hostname 0.0.0.0 --port 3000"]
