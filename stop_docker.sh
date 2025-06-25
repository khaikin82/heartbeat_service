#!/bin/bash

CONTAINER_NAME="heartbeat_service_container"

if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
  echo "[~] Stopping container: $CONTAINER_NAME"
  docker stop $CONTAINER_NAME
  docker rm $CONTAINER_NAME
  echo "[✓] Stopped and removed $CONTAINER_NAME"
else
  echo "[i] No running container named $CONTAINER_NAME found."
fi
