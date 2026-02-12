# Use Node base image
FROM node:20-slim

# 1. Install Python + venv tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Backend setup (Virtual Env to fix PEP 668)
COPY pyproject.toml uv.lock ./
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip
RUN /opt/venv/bin/pip install .

# 3. Frontend setup (Next.js)
WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build

# 4. Final Prep
WORKDIR /app
COPY . .

# Expose port
EXPOSE 3000

# 5. Start command (Both Backend Agent & Frontend Web)
# Note: Using 'npm start' instead of 'serve' because Next.js API routes (token) require the server.
CMD ["/bin/bash", "-c", "source /opt/venv/bin/activate && python src/agent.py start & npm --prefix web start -- --hostname 0.0.0.0 --port 3000"]
