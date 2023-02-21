#!/bin/bash -x

#
# Install services related to power management and jobs clean up
#

install srv/printer_power_manager.py /usr/local/bin/
install srv/printer_startup_cleanup_after_server.sh /usr/local/bin/

install --mode=644 srv/printer_power_manager.service /etc/systemd/system/
install --mode=644 srv/printer_startup_cleanup_after_server.service /etc/systemd/system/

systemctl daemon-reload

systemctl enable printer_power_manager.service
systemctl start printer_power_manager.service

systemctl enable printer_startup_cleanup_after_server.service
systemctl start printer_startup_cleanup_after_server.service

