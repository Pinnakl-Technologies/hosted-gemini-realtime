FROM python:3.11-slim

# System deps: we need Node.js, npm, and build tools
# Note: nodejs from debian slim is often older, but 18+ is usually available in newer slims or can be added.
# For 3.11-slim (Bookworm), it provides Node.js 18.
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Working dir
WORKDIR /app

# 1. Backend Prep
# Copy core Python files
COPY pyproject.toml .
COPY requirements-docker.txt ./requirements.txt
COPY src ./src

# Install Python deps
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 2. Frontend Prep
# Copy web folder
COPY web ./web
WORKDIR /app/web

# Install Node.js dependencies and build
# This will use the .env.local found in web/ if present
RUN npm install
RUN npm run build

# 3. Final configuration
# Move back to root
WORKDIR /app

# Expose Next.js port
EXPOSE 3000

# Start both services parallel in a single container
# - 'npm start' in web/
# - 'python src/agent.py dev' in root
# We use & to background the first and then run the second
# 'cd web && npm start' handles the frontend
# 'python src/agent.py dev' handles the agent
CMD ["sh", "-c", "cd web && npm start & python src/agent.py dev"]
