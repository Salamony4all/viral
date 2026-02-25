# Use the official Microsoft Playwright Python image
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Install additional system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app
# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install playwright browser
RUN playwright install chromium

# Copy the rest of the application code
COPY . .

# Create workspace directories
RUN mkdir -p workspace/trends workspace/assets workspace/render workspace/review logs

# Expose the port the app runs on
EXPOSE 8000

# Environment variables
ENV PORT=8000
ENV LOG_LEVEL=INFO

# Run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
