#!/bin/bash

# Stop and remove all containers
docker stop $(docker ps -aq) -f
docker rm $(docker ps -aq) -f

# Remove all images
docker rmi -f $(docker images -aq)

# Remove all volumes
docker volume rm -f $(docker volume ls -q)

# Remove all networks except the default ones (bridge, host, none)
docker network rm $(docker network ls | grep -v "bridge\|host\|none" | awk '/ / { print $1 }')

# Prune the system (remove unused data like images, containers, volumes, and networks)
docker system prune -a --volumes -f

echo "Docker cleanup complete!"