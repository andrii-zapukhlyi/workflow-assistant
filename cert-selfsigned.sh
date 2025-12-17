#!/bin/bash

DOMAIN_OR_IP="YOUR_IP_ADDRESS" # REPLACE with your IP
DATA_PATH="./data/certbot"
CONF_PATH="$DATA_PATH/conf/live/$DOMAIN_OR_IP"

echo "### Creating self-signed certificate for $DOMAIN_OR_IP ..."

mkdir -p "$CONF_PATH"
mkdir -p "$DATA_PATH/conf"

if [ ! -e "$DATA_PATH/conf/ssl-dhparams.pem" ]; then
    openssl dhparam -out "$DATA_PATH/conf/ssl-dhparams.pem" 2048
fi

if [ ! -e "$DATA_PATH/conf/options-ssl-nginx.conf" ]; then
    curl -s -L https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$DATA_PATH/conf/options-ssl-nginx.conf"
fi

openssl req -x509 -nodes -newkey rsa:4096 -days 3650 \
  -keyout "$CONF_PATH/privkey.pem" \
  -out "$CONF_PATH/fullchain.pem" \
  -subj "/CN=$DOMAIN_OR_IP"

echo
echo "### Certificate created at: $CONF_PATH"
echo "### You can now start Nginx with: docker compose -f docker-compose.prod.yml up -d"