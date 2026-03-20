# Use an official, lightweight Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables to ensure Python output is logged immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire current directory contents into the container at /app
COPY . /app

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Command to run the FastAPI application
# We run it as a module from the root so the relative imports (..1_intent_layer) work perfectly
CMD ["uvicorn", "api.gateway_v2:app", "--host", "0.0.0.0", "--port", "8000"]
