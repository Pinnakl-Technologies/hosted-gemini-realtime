# Use Node.js 20 as the base image
FROM node:20-slim

# Install system dependencies and Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# Copy root Python files first for caching
COPY pyproject.toml uv.lock ./
RUN uv pip install --system .

# Copy web files and build
COPY web/package*.json ./web/
WORKDIR /app/web
RUN npm ci
COPY web/ ./
RUN npm run build

# Copy everything else
WORKDIR /app
COPY . .

# Expose Next.js port
EXPOSE 3000

# Start both backend agent and frontend web using concurrently
CMD npx concurrently -n "agent,web" -c "cyan,magenta" \
    "python src/agent.py start" \
    "npm --prefix web start -- --hostname 0.0.0.0 --port $PORT"
