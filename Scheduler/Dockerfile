# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Specify the entry point to the FastAPI application
ENTRYPOINT ["uvicorn"]

# Pass the command arguments
CMD ["app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

