FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the necessary directories
RUN mkdir -p utilities static

# Copy application files
COPY app.py .
COPY custom.css .
COPY utilities/ ./utilities/
COPY static/ ./static/

# Expose the port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Add a healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/ || exit 1

# Run the application
CMD ["python", "app.py"] 