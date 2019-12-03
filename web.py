import threading

from flask import Flask, render_template, request, send_file
from server import BT_Server
from flask_qrcode import QRcode

from RSA_Util import *

app = Flask(__name__)
qrcode = QRcode(app)

rsa = RSA_Util()
server = BT_Server(rsa)


@app.route("/")
def home():
    return "Hello, World!"


@app.route("/run")
def run():
    print(server.isRunning)
    if server.isRunning:
        return "Server already running"
    else:
        threading.Thread(target=server.run_server).start()
        return "server running"


def get_mac():
    import subprocess

    cmd = "hciconfig"
    device_id = "hci0"
    status, output = subprocess.getstatusoutput(cmd)
    bt_mac = output.split("{}:".format(device_id))[1].split("BD Address: ")[1].split(" ")[0].strip()
    return bt_mac


@app.route("/qrcode", methods=["GET"])
def get_qrcode():
    data = get_mac() + "\n"
    data += rsa.get_public_key_base64()
    return render_template("qrcode.html", qrcode_img=qrcode(data))


if __name__ == "__main__":
    app.run(debug=True)
