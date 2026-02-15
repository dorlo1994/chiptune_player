# Use slim Python image
FROM python:3.12-slim

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system deps only if needed (none required now)
# RUN apt-get update && apt-get install -y ...

# Copy dependency file first (better layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Add src to Python path
ENV PYTHONPATH=/app/src

# Expose FastAPI port
EXPOSE 8000

# Start server (adjust module path if needed)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]

