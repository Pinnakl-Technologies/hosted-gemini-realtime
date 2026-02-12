FROM node:20-slim

# Install Python for backend
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Create Python virtualenv for backend
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip
RUN /opt/venv/bin/pip install .

# Build frontend (Next.js)
WORKDIR /app/web
RUN npm install
RUN npm run build

# Go back to /app
WORKDIR /app

# Start both frontend + backend
# & runs frontend in background so backend starts too
CMD bash -c "cd web && npx next start --hostname 0.0.0.0 --port 3000 & cd ../src && /opt/venv/bin/python agent.py start"
