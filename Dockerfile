# Dockerfile

# --- Build Stage ---
# Use an official Python runtime as a parent image
FROM python:3.13-slim as builder

# Set the working directory
WORKDIR /usr/src/app

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure python output is sent straight to the terminal
ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Final Stage ---
# Create a new, clean image
FROM python:3.13-slim

# RUN apt-get update && apt-get install -y curl wget && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    appuser

# Set the working directory
WORKDIR /usr/src/app

# Copy pre-built wheels and install them
COPY --from=builder /usr/src/app/wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy the application code
COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini .
COPY seed.py .

# Change ownership to the non-root user
RUN chown -R appuser:appuser /usr/src/app
USER appuser

# Command to run the application using a production-grade server
# This will be overridden by Coolify's start command, but it's good practice to have it.
CMD uvicorn app.main:app --host 0.0.0.0 --port 80