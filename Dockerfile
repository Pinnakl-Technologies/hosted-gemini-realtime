FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y nodejs npm curl build-essential && rm -rf /var/lib/apt/lists/*

# Working dir
WORKDIR /app

# Copy Python files
COPY pyproject.toml .
COPY requirements.txt .
COPY src ./src

# Install Python deps
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy frontend
COPY web ./web
WORKDIR /app/web
RUN npm install
RUN npm run build

# Expose ports
EXPOSE 3000
EXPOSE 38623

# Start both services
WORKDIR /app
CMD ["sh", "-c", "cd web && npm start & python src/agent.py dev"]
