#!/bin/bash
mkdir -p ./nginx/certs

if [ ! -f ./nginx/certs/nginx-selfsigned.key ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ./nginx/certs/nginx-selfsigned.key \
        -out ./nginx/certs/nginx-selfsigned.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"
    echo "Certificates generated."
else
    echo "Certificates already exist."
fi
