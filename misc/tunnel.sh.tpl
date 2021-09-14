#! /bin/bash

ssh -i {tunnel_keyfile} \
    -o StrictHostKeyChecking=no \
    -R 0.0.0.0:8080:localhost:8080 \
    -R 0.0.0.0:5000:localhost:5000 \
    -TN tunneluser@{tunnel_ip}
