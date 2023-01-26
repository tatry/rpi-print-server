#!/bin/bash

# Purge all jobs - must be executed on running CUPS server
cancel -a -x

# These must be done when CUPS is not running
#systemctl stop cups.service
# Remove logs
#rm -rf /var/log/cups/*
# Restart job counter
#rm -f /var/cache/cups/job.cache
#systemctl start cups.service
