# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl build-essential nodejs npm git && \
    rm -rf /var/lib/apt/lists/*

# Install uv package manager globally
RUN pip install --upgrade pip
RUN pip install uv

# Install concurrently globally
RUN npm install -g concurrently

# Copy Python agent
COPY pyproject.toml .
COPY src ./src

# Install Python dependencies
RUN uv sync

# Copy frontend
COPY web ./web
WORKDIR /app/web

# Install Node.js dependencies
RUN npm install
RUN npm run build

# Expose ports
EXPOSE 3000
EXPOSE 38623

# Start both frontend + agent
WORKDIR /app
CMD ["sh", "-c", "concurrently \"uv run python src/agent.py start\" \"cd web && npm start\""]
