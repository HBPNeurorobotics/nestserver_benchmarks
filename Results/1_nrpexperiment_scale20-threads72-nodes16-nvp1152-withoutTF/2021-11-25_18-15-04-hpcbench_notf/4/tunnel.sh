#! /bin/bash

ssh -i $HOME/bf_data/key-tunneluser \
    -o StrictHostKeyChecking=no \
    -R 0.0.0.0:8080:localhost:8080 \
    -R 0.0.0.0:5000:localhost:5000 \
    -TN tunneluser@148.187.148.198
