#!/bin/bash
set -e

/bin/bash -c "python3 /home/$user/src/external_viz_manager/manage.py makemigrations"
/bin/bash -c "python3 /home/$user/src/external_viz_manager/manage.py migrate"
/bin/bash -c "python3 /home/$user/src/external_viz_manager/manage.py create_superuser"

# Start Supervisor
sudo -E supervisord -n -c /etc/supervisord.conf
