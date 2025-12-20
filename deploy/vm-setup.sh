#!/bin/bash

## Add Swap Space for small VMS
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

## Install Docker
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER

sudo update-ca-certificates
sudo systemctl restart docker

## REPLACE WITH YOUR ACTUAL REGISTRY NAME (e.g., workflowassistantacr)
ACR_NAME="your-acr-name" 

## Login to ACR and pull images
docker login $ACR_NAME.azurecr.io
docker pull $ACR_NAME.azurecr.io/workflow-assistant-backend:latest
docker pull $ACR_NAME.azurecr.io/workflow-assistant-frontend:latest

## Generate Let's Encrypt certificate
chmod +x cert-letsencrypt.sh
rm -vf ./data/certbot/conf/ssl-dhparams.pem
./cert-letsencrypt.sh

docker ps