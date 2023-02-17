# Base image
FROM python:3.8-slim-buster

# Install required packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the Python script and configuration files
COPY bot.py config.ini ./

# Install the required Python packages
RUN pip install -r requirements.txt

# Expose the required ports
EXPOSE 8080

# Set the entrypoint command
CMD ["python", "bot.py"]
