# bluetoothTest


sudo apt-get install cryfs # because I just want to Cry 


# sudo apt-get install bluetooth libbluetooth-dev
# sudo apt install bluez


'''modifying /etc/systemd/system/dbus-org.bluez.service,

changing

ExecStart=/usr/lib/bluetooth/bluetoothd

into

ExecStart=/usr/lib/bluetooth/bluetoothd -C

Then adding the Serial Port Profile, executing: sudo sdptool add SP

Make sure you run the following after doing this:
    1. systemctl daemon-reload
    2. service bluetooth restar
'''
