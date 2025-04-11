#!/bin/bash

# Check if .env file exists, create from example if not
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️ Please edit the .env file to add your OpenAI API key!"
fi

# Build and start the application
echo "Starting Perfect Date Generator..."
docker-compose up --build -d

# Display information about accessing the app
echo "✅ Perfect Date Generator is now running!"
echo "🌐 Access the app at: http://localhost:${PORT:-7860}"
echo "📝 Logs can be viewed with: docker-compose logs -f"
echo "🛑 To stop the app: docker-compose down" 