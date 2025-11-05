#!/bin/bash
set -e

IMAGE_NAME="meeting-summarizer"

# Check if test mode
if [ "$1" = "test" ]; then
    echo "Running in TEST mode (1 minute audio only)..."
    TEST_MODE="true"
else
    echo "Running in FULL mode..."
    TEST_MODE="false"
fi

# Build Docker image
echo "Building Docker image..."
docker build -f docker/Dockerfile -t $IMAGE_NAME .

# Run container
echo "Starting processing..."
docker run --rm \
    -v "$(pwd)/input:/app/input" \
    -v "$(pwd)/output:/app/output" \
    -v "$(pwd)/config.yaml:/app/config.yaml" \
    -e TEST_MODE=$TEST_MODE \
    $IMAGE_NAME

echo ""
echo "Done! Check the output/ directory for results."
