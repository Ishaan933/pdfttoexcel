# Base image with Python and Java pre-installed
FROM openjdk:11-jdk-slim

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the app's port
EXPOSE 5000

# Start the Flask application
CMD ["python3", "app.py"]
