#!/bin/bash
set -e

# Start Supervisor
sudo -E supervisord -n -c /etc/supervisord.conf
