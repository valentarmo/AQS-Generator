#!/bin/bash
docker pull fighur/AQSDataGenerator:latest
$CONTAINER_ID=$(docker run -d -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION fighur/AQSDataGenerator:latest)