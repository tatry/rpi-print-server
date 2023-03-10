#!/bin/bash

if [ `id -u` -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

set -x

USER=printer
THIS_REPO=`pwd`
DRIVER_REPO="/opt/pi-parport"
PYCUPS_NOTIFY_REPO="/opt/pycups-notify"
# For available locales see file /usr/share/i18n/SUPPORTED
LOCALE="pl_PL.UTF-8"

#
# Update system
#

apt update
apt -y upgrade

#
# Configure system
#

sed -i "/$LOCALE/s/^# //" /etc/locale.gen
locale-gen
localectl set-locale LANG="$LOCALE"

# Disable Bluetooth
systemctl disable hciuart
echo "dtoverlay=disable-bt" >> /boot/config.txt

# Lower GPU memory
echo "gpu_mem=16" >> /boot/config.txt

#
# Install dependencies and packages
#

apt install -y \
               git \
               raspberrypi-kernel-headers \
               python3-pip \
               libcups2-dev \
               cups \
               hplip \
               dkms

apt -y autoremove
apt clean
pip3 cache purge

#
# Configure dependencies
#

usermod -aG lpadmin "$USER"

#
# Install pycups-notify from source
#

git clone https://github.com/anxuae/pycups-notify "$PYCUPS_NOTIFY_REPO"
cd "$PYCUPS_NOTIFY_REPO"
git checkout 4f507cccdfb7e2f8b622425eba10ba6f9248514a
python setup.py install

#
# Install LPT drivers
#

git clone https://github.com/tatry/pi-parport "$DRIVER_REPO"

cd "$DRIVER_REPO"
./install.sh

#
# Configure CUPS
#

cd "$THIS_REPO"
install --mode=640 --group=lp --owner=root srv/cupsd.conf /etc/cups/cupsd.conf
systemctl restart cups.service

#
# Install services related to power management and jobs clean up
#

cd "$THIS_REPO"

install srv/printer_power_manager.py /usr/local/bin/
install srv/printer_startup_cleanup_after_server.sh /usr/local/bin/

install --mode=644 srv/printer_power_manager.service /etc/systemd/system/
install --mode=644 srv/printer_startup_cleanup_after_server.service /etc/systemd/system/

systemctl daemon-reload

systemctl enable printer_power_manager.service
systemctl start printer_power_manager.service

systemctl enable printer_startup_cleanup_after_server.service
systemctl start printer_startup_cleanup_after_server.service

reboot

