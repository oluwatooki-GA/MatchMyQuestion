FROM python:3.12-slim

WORKDIR /app

# Install sysem dependencies


# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with timeout and retry
RUN pip install --no-cache-dir --timeout=1000 --retries=10 -r requirements.txt

# Copy source code
COPY . .

# Default command (override as needed)
CMD ["python", "-m", "app.main"]
