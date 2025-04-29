# Use Python base image
FROM python:3.9-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc build-essential && apt-get clean

# Install Python dependencies
COPY packages.txt /app/
RUN pip install --no-cache-dir -r packages.txt

# Copy project files
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
