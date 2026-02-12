# 1️⃣ Base Node + Python image
FROM node:20-slim

# 2️⃣ Install Python dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-venv python3-pip curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3️⃣ Set app working directory
WORKDIR /app

# 4️⃣ Copy everything
COPY . .

# 5️⃣ Setup Python virtual environment for agent
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip
RUN /opt/venv/bin/pip install .

# 6️⃣ Build frontend
WORKDIR /app/web
RUN npm install
RUN npm run build

# 7️⃣ Start both backend + frontend
WORKDIR /app
CMD bash -c "/opt/venv/bin/python src/agent.py dev & cd web && npx next start --hostname 0.0.0.0 --port 3000"
