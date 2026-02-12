# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl build-essential nodejs npm git && \
    rm -rf /var/lib/apt/lists/*

# Install uv for Python dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Install concurrently globally
RUN npm install -g concurrently

# Copy Python agent
COPY pyproject.toml .
COPY src ./src

# Setup Python virtual env
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install .

# Copy frontend
COPY web ./web
WORKDIR /app/web

# Install Node.js dependencies
RUN npm install
RUN npm run build

# Expose ports
EXPOSE 3000
EXPOSE 38623

# Set root working directory
WORKDIR /app

# Command to run both frontend + agent
CMD ["sh", "-c", "concurrently \"uv run python src/agent.py dev\" \"cd web && npm start\""]
