FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the necessary directories
RUN mkdir -p utilities

# Copy application files
COPY app.py .
COPY custom.css .
COPY utilities/ ./utilities/

# Expose the port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"] 