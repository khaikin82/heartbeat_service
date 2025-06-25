#!/bin/bash

# Tên image và container
IMAGE_NAME="heartbeat_service_image"
CONTAINER_NAME="heartbeat_service_container"

# Build image từ Dockerfile hiện tại
echo "[+] Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME .

# Stop và remove container cũ nếu đang chạy
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
  echo "[~] Stopping and removing old container: $CONTAINER_NAME"
  docker stop $CONTAINER_NAME
  docker rm $CONTAINER_NAME
fi

# Run container mới
echo "[+] Running container: $CONTAINER_NAME"
docker run -d \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  $IMAGE_NAME
