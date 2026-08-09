# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend codebase into the container
COPY . .

# Ensure the data directory exists
RUN mkdir -p data

# Pre-download SentenceTransformer model during build to prevent massive cold-start delays on Render
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

# Expose port 8000
EXPOSE 8000

# Define environment variable
ENV PORT=8000
ENV HOST=0.0.0.0

# Run uvicorn server
CMD ["sh", "-c", "uvicorn app:app --host $HOST --port $PORT"]
