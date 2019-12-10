import threading

from flask import Flask, render_template, request, send_file, url_for
from server import BT_Server
from flask_qrcode import QRcode

import time

import tkinter as tk
from tkinter import filedialog
import easygui

from RSA_Util import *
from bluetooth import *

app = Flask(__name__)
qrcode = QRcode(app)

rsa = RSA_Util()
server = BT_Server(rsa)


@app.route("/")
def home():
    run()
    return render_template("index.html", device_name=server.device_name, is_running=server.isRunning)


@app.route("/manage-devices")
def manage_devices():
    return render_template("manage-devices.html", device_name=server.device_name, is_running=server.isRunning)


def get_mac():
    import subprocess

    cmd = "hciconfig"
    device_id = "hci0"
    status, output = subprocess.getstatusoutput(cmd)
    bt_mac = output.split("{}:".format(device_id))[1].split("BD Address: ")[1].split(" ")[0].strip()
    return bt_mac


def qr_code(mode):
    data = get_mac() + "\n"
    data += rsa.get_public_key_base64() + "\n"
    data += mode
    return render_template("qr-code.html", qrcode_img=qrcode(data), device_name=server.device_name,
                           is_running=server.isRunning)


@app.route("/qr-code", methods=["GET"])
def qr_code_normal():
    return qr_code("normal")


@app.route("/qr-code-share", methods=["GET"])
def qr_code_share():
    threading.Thread(target=server.create_server_sharing).start()
    return qr_code("share")


@app.route("/manage-folders")
def manage_folders():
    return render_template("manage-folders.html", device_name=server.device_name, is_running=server.isRunning,
                           folders=server.list_folders())


@app.route("/share-folders")
def share_folders():
    return render_template("share-folders.html", device_name=server.device_name, is_running=server.isRunning)


@app.route("/add_folder", methods=["GET"])
def add_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    root.destroy()

    if not folder_path:  # no folder path stop
        return "ok", 200

    proceed = easygui.ccbox(f"Are you sure you want to encrypt: {folder_path}",title='Confirm path folder') 

    if proceed:
        server.add_folder(folder_path)
    
        return "ok", 200
    else:
        return "ok", 200



# @app.route("/add_device")
# def add_device():
#     print("here")
#     server.add_device()
#     return "ok", 200


@app.route('/disconnect')
def disconnect():
    server.disconnect()
    return "ok", 200


@app.route('/device_update_keys')
def update_keys():
    server.update_keys()
    return "ok", 200


@app.route('/remove_device')
def remove_device():
    server.remove_device()
    return "ok", 200

@app.route("/remove_folder", methods=["GET"])
def remove_folder():
    remove_path = request.args.get("remove_path")
    print(f"Removing encryption from {remove_path}")

    if not remove_path:
        return 'invalid path',403
    
    resp = server.remove_folder(remove_path)

    if resp:
        return 'ok',200
    else:
        return 'Error on removing', 403

@app.route('/test')
def test():
    s = ""
    for e in server.list_folders():
        s += e + "\n"
    return s, 200


def run():
    if not server.isRunning:
        threading.Thread(target=server.run_server).start()


if __name__ == "__main__":
    app.run(debug=True)
