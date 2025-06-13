# Use Python 3.11+ as the base image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app/src

# Copy requirements file
COPY requirements.txt ..

# Install dependencies
RUN pip install --no-cache-dir -r ../requirements.txt

# Copy the source code
COPY src/ .
COPY resources/ ../resources/

# Set Python-specific environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Copy environment file
COPY .env ../.env

# Expose the port your FastAPI app will run on
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]