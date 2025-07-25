#!/bin/bash
# Script to format Python code using Black and isort

# Exit on error
set -e

echo "Formatting Python code..."

# Check if Black and isort are installed
if ! command -v black &> /dev/null; then
    echo "Black not found. Installing..."
    pip install black
fi

if ! command -v isort &> /dev/null; then
    echo "isort not found. Installing..."
    pip install isort
fi

# Format with Black
echo "Running Black..."
black .

# Sort imports with isort
echo "Running isort..."
isort .

echo "Code formatting complete!"