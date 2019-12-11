# bluetoothTest

# Dependencies
Install the following packages
```bash
sudo apt-get install bluetooth libbluetooth-dev bluez cryfs gcc
```
### To use bluetooth without root you need to
modify ```/etc/systemd/system/dbus-org.bluez.service```,

by changing
```
ExecStart=/usr/lib/bluetooth/bluetoothd
```
into
```
ExecStart=/usr/lib/bluetooth/bluetoothd -C
```

### Make sure you run the following after doing this:
```bash
sudo usermod -G bluetooth -a $USERNAME

sudo sdptool add SP
sudo systemctl daemon-reload
sudo systemctl restart bluetooth

sudo chgrp bluetooth /var/run/sdp
sudo systemctl daemon-reload
```

#### (You might need to restart the computer for bluetooth to be in users groups)

Do this everytime before running the script (or make it start on boot)
```bash
sudo chgrp bluetooth /var/run/sdp
```
## To install python requirements
```bash
pip install -r requirements.txt
```


To run the program you should use at least python 3.6, chrome and linux(tested on Ubuntu)
