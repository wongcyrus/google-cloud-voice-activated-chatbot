# Dockerfile
# Base image
FROM python:3.11.5-slim
# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Set environment variables
ENV PORT=8000

RUN apt-get update && apt-get install -y ffmpeg

# Set working directory
WORKDIR /model

# Copy files to /model
COPY . .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD uvicorn --host 0.0.0.0 --port $PORT app:app