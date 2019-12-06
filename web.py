import threading

from flask import Flask, render_template, request, send_file, url_for
from server import BT_Server
from flask_qrcode import QRcode

from RSA_Util import *
from bluetooth import *

app = Flask(__name__)
qrcode = QRcode(app)

rsa = RSA_Util()
server = BT_Server(rsa)

device_name = ''
device_addr = last_device_addr = None
first = True


def get_device_name():
    print("Finding connection...")
    nearby_devices = discover_devices(lookup_names=True)
    print("%d devices found" % len(nearby_devices))

    for addr, name in nearby_devices:
        print("Found %s  (%s)" % (name, addr))
        if addr == device_addr:
            print("Connected to %s  (%s)\n" % (name, addr))
            return name

    if device_name == '' and device_addr is not None:
        print("Connection not found.\nRepeating...\n")
        return get_device_name()

    elif device_addr is None:
        return ''


def update_device_name():
    global device_name

    print("================")
    print(last_device_addr)
    print(device_addr)
    print(device_name)

    if device_addr is None:
        device_name = ''

    elif last_device_addr != device_addr or first is True:
        device_name = get_device_name()


@app.route("/")
def home():
    update_device_name()
    return render_template("index.html", device_name=device_name)


@app.route("/manage-devices")
def manageDevices():
    update_device_name()

    return render_template("manage-devices.html", device_name=device_name)


def get_mac():
    import subprocess

    cmd = "hciconfig"
    device_id = "hci0"
    status, output = subprocess.getstatusoutput(cmd)
    bt_mac = output.split("{}:".format(device_id))[1].split("BD Address: ")[1].split(" ")[0].strip()
    return bt_mac


@app.route("/qr-code", methods=["GET"])
def qrCode():
    data = get_mac() + "\n"
    data += rsa.get_public_key_base64()
    update_device_name()
    return render_template("qr-code.html", qrcode_img=qrcode(data), device_name=device_name)


@app.route("/manage-files")
def manageFiles():
    update_device_name()

    return render_template("manage-files.html", device_name=device_name)


@app.route("/run")
def run():
    global device_addr, last_device_addr, first

    print(server.isRunning)

    if server.isRunning:
        print("Server is already running!")
        last_device_addr = device_addr
        device_addr = server.deviceAddress
        first = False

    else:
        t = threading.Thread(target=server.create_server())
        t.start()

        # wait for the device address to be set
        t.join()

        last_device_addr = server.deviceAddress
        device_addr = server.deviceAddress
        first = True

        t2 = threading.Thread(target=server.run_server())
        t2.start()
        print("Vou continuar! yupi")  # FIXME ele não continua, temos que dar refresh logo a seguir

    return render_template("run-server.html")


if __name__ == "__main__":
    app.run(debug=True)
