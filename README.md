# rpi-print-server

Installation and configuration of print server on Raspberry Pi with printer manager (power on/off). An old printer on LPT port is assumed.

Adjust configuration in files:
- `srv/printer_power_manager.py`
- `srv/cupsd.conf`
- `install.sh`

and then follow procesure below or just call `sudo ./install.sh` after paragraph 4 in section System installation.

# System installation

1. Write Raspberry Pi OS on a SD card (e.g. using Raspberry Pi Imager)
2. Boot RPi and do basic configuration.
3. When logged in, validate configuration like:
   - Locale and keyboard layout.
   - Network connectivity.
   - Enabled and running SSH server.
4. Disable GUI and reboot (to check if land on shell).
5. Remove some unnecessary packages:
   ```shell
   sudo apt purge chromium-browser geany vlc
   sudo apt autoremove
   ```
6. Update system:
   ```shell
   sudo apt update
   sudo apt upgrade
   sudo reboot
   ```
7. Install necessary packages:
   ```shell
   sudo apt install git raspberrypi-kernel-headers python3-pip libcups2-dev 
   ```
8. Block updates of kernel:
   ```shell
   sudo apt-mark hold libraspberrypi-bin libraspberrypi-dev libraspberrypi-doc libraspberrypi0
   sudo apt-mark hold raspberrypi-bootloader raspberrypi-kernel raspberrypi-kernel-headers
   ```
9. Configure static IP address on DHCP server.
 
# Connect printer

Beacuse of LPT printer, let's see [pi-parport](https://github.com/tatry/pi-parport) repository. First you have to build hardware
(latest version) and test it for shorcircuits. Next make it HAT by writing right values to EEPROM memory using
[instruction](https://github.com/tatry/pi-parport/tree/master/eeprom).

Next follow [README.md](https://github.com/tatry/pi-parport/blob/master/README.md) to install drivers and DTO.

Add `ppdev` and `lp` modules to `/etc/modules` to expose LPT port to user space.

After reboot `lp` and `ppdev` were automatically loaded.

# CUPS configuration

Install cups if not already installed: `sudo apt install cups hplip`.
Also add user to `lpadmin` group: `sudo usermod -aG lpadmin printer`

1. Edit CUPS configuration file `/etc/cups/cupsd.conf` to allow remote access and administration. Important fragments of the file should look like this:
   ```
   # Allow remote access
   Port 631
   Listen /run/cups/cups.sock
   ```
   ```
   <Location />
     # Allow remote access...
     Order allow,deny
     Allow all
   </Location>
   <Location /admin>
     AuthType Default
     Require user @SYSTEM
   </Location>
   <Location /admin/conf>
     AuthType Default
     Require user @SYSTEM
   </Location>
   <Location /admin/log>
     AuthType Default
     Require user @SYSTEM
   </Location>
   ```
2. Adjust CUPS server configuration. Open web panel (IP:631) and go to Administration section. In server options expand Advance options and
   make sure to check following options:
   - Share printers connected to this system.
   - Allow printing from the Internet.
   - Allow users to cancel any job (not just their own).
   Click "Change setting" button.
3. Add printer in a standard manner.

# Install and configure printer managers

Printer power is enabled/disabled by GPIO pin, an external device is required with relay.

Printer is automatically power on when created a new job and power it off after some time.

Install dependencies:
```shell
sudo pip3 install --system pycups-notify
sudo pip3 cache purge
```

Now edit scripts with correct GPIO pin. Then install management scripts:
```shell
install srv/printer_power_manager.py /usr/local/bin/
install srv/printer_startup_cleanup_after_server.sh /usr/local/bin/

install --mode=644 srv/printer_power_manager.service /etc/systemd/system/
install --mode=644 srv/printer_startup_cleanup_after_server.service /etc/systemd/system/

systemctl daemon-reload

systemctl enable printer_power_manager.service
systemctl start printer_power_manager.service

systemctl enable printer_startup_cleanup_after_server.service
systemctl start printer_startup_cleanup_after_server.service
```

