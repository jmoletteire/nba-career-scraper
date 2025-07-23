#!/bin/bash

# NBA Career Scraper Runner Script

# Change to the script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please copy .env.example to .env and configure your settings."
    echo "cp .env.example .env"
    exit 1
fi

# Install dependencies if needed
echo "Checking dependencies..."
pip install -r requirements.txt

# Create required directories
mkdir -p logs data

# Run the scraper
echo "Starting NBA Career Scraper..."

if [ "$1" = "--periodic" ]; then
    echo "Running in periodic mode..."
    python src/main.py --periodic "${2:-24}"
else
    echo "Running single check..."
    python src/main.py
fi
