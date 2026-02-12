# Use slim Python base
FROM python:3.11-slim

# Install Node.js, npm, curl, build tools
RUN apt-get update && \
    apt-get install -y nodejs npm curl build-essential git && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only essential Python files first to leverage caching
COPY src/pyproject.toml src/requirements.txt ./src/

# Install only essential Python dependencies
RUN pip install --upgrade pip && \
    pip install -r src/requirements.txt

# Copy the rest of your project
COPY src ./src
COPY web ./web

# Copy .env.local files (Ensuring they are available for both runtime environments)
COPY src/.env.local ./src/.env.local
COPY web/.env.local ./web/.env.local

# Set environment variables for Node.js
ENV NODE_ENV=development
WORKDIR /app/web

# Install Node dependencies and build frontend
RUN npm install && npm run build

# Expose ports
EXPOSE 3000 8000 8765

# Default startup command
# - Runs the Python agent in the background
# - Runs the Next.js frontend in the foreground
CMD ["sh", "-c", "cd ../src && python agent.py dev & cd ../web && npm run dev"]
