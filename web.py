import threading

from flask import Flask, render_template, request, send_file, url_for
from server import BT_Server
from flask_qrcode import QRcode

from RSA_Util import *

app = Flask(__name__)
qrcode = QRcode(app)

rsa = RSA_Util()
server = BT_Server(rsa)


@app.route("/")
def home():
    return render_template("index.html", device_name='') #FIXME pass device-name


@app.route("/manage-devices")
def manageDevices():
    return render_template("manage-devices.html", device_name='') #FIXME pass device-name


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
    return render_template("qr-code.html", qrcode_img=qrcode(data), device_name='') #FIXME pass device-name


@app.route("/manage-files")
def manageFiles():
    return render_template("manage-files.html", device_name='') #FIXME pass device-name


@app.route("/run")
def run():
    print(server.isRunning)
    if server.isRunning:
        return "Server already running"
    else:
        threading.Thread(target=server.run_server).start()
        return "server running"


if __name__ == "__main__":
    app.run(debug=True)
