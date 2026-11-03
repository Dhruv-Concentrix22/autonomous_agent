FROM python:3.11-slim

WORKDIR /app

# Install pytest and Antigravity SDK inside the isolated container
RUN pip install --no-cache-dir pytest google-antigravity python-dotenv

# Copy all problem files and the harness script into the container workspace
COPY buggy_code.py /app/
COPY test_buggy_code.py /app/
COPY harness.py /app/

# By default, run the harness inside the container
CMD ["python", "harness.py"]
