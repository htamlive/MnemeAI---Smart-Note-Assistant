#!/bin/bash

# Check if Docker is available, if not, install Docker
if ! command -v docker &>/dev/null; then
    echo "Docker not found. Please install Docker to continue."
    # Install Docker (example command, might vary depending on your OS)
    # Insert your Docker installation command here
    exit 1
fi

# Check if the PostgreSQL Docker image exists
if ! docker image inspect postgres:latest &>/dev/null; then
    echo "PostgreSQL image not found. Pulling the latest PostgreSQL image..."
    docker pull postgres:latest
fi

# Run a PostgreSQL container if not already running
if ! docker ps -a --format '{{.Names}}' | grep -q '^smart-note-assistant$'; then
    echo "Initializing PostgreSQL container for the smart-note-assistant database..."
    docker run -d --name smart-note-assistant -e POSTGRES_DB=note_persistence -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:latest
    echo "PostgreSQL container for note_persistence database initialized."
    echo "Please run the table creation script to create the necessary tables."
else
    echo "PostgreSQL container for smart-note-assistant database already exists."
fi
