# Base image for Node + Python
FROM node:20-slim

# Install Python + build tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtualenv for backend
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install backend dependencies
RUN pip install --upgrade pip
RUN pip install .

# Install frontend dependencies
WORKDIR /app/web
RUN npm install
RUN npm run build

# Start both backend and frontend
WORKDIR /app
CMD ["sh", "-c", "python src/agent.py start & cd web && npx next start --hostname 0.0.0.0 --port $PORT"]
