# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependency file and install packages
COPY requirements.txt .
COPY config.env .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all other project files
COPY . .

# Expose the Flask port
EXPOSE 5000

# Default command to run the app
CMD ["python", "main.py"]