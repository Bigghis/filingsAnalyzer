FROM python:3.12-slim

WORKDIR /app

# Install Redis
RUN apt-get update && apt-get install -y redis-server && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and setup files
COPY requirements.txt .
COPY setup.py .

# Copy source code
COPY src/ ./src/

# Install dependencies and the package
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# Create a startup script
COPY start.sh .
RUN chmod +x start.sh

# Default command
CMD ["./start.sh"]
