#!/bin/bash

# Permissions: chmod +x deploy.sh

# Step 1: Pull from the repository
echo "Step 1: Pulling from the repository..."
git pull

# Step 2: Re-build the Docker image
echo "Step 2: Re-building the Docker image..."
docker-compose build fastapi

# Step 3: Restart the containers
echo "Step 3: Restarting the containers..."
docker-compose up -d
