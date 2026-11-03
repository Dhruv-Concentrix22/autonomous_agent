FROM python:3.11-slim

# Install git so the container can clone and push repositories
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies: pytest, antigravity, dotenv, and PyGithub for PR creation
RUN pip install --no-cache-dir pytest google-antigravity python-dotenv PyGithub

# Copy application files into the container workspace
COPY tools.py /app/
COPY harness.py /app/

# By default, run the harness inside the container
CMD ["python", "harness.py"]
