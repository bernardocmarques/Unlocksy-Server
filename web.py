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
    return render_template("index.html", device_name=server.device_name, is_running=server.isRunning,
                           proximity=server.isProximityActivated)


@app.route("/update_proximity", methods=["POST"])
def update_proximity():
    server.isProximityActivated = True if request.form.get('proximity') == 'True' else False
    print("Proximity enabled!") if server.isProximityActivated is True else print("Proximity disabled")
    home()
    return "ok", 200


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


def get_qr_code_data(mode):
    data = get_mac() + "\n"
    data += rsa.get_public_key_base64() + "\n"
    data += mode
    return data


@app.route("/qr-code", methods=["GET"])
def qr_code_normal():
    return render_template("qr-code.html", qrcode_img=qrcode(get_qr_code_data("normal")),
                           device_name=server.device_name, is_running=server.isRunning)


@app.route("/qr-code-share", methods=["GET"])
def qr_code_share():
    return render_template("qr-code-share.html", qrcode_img=qrcode(get_qr_code_data("share")),
                           is_running=server.isRunning)


@app.route("/folder-manager")
def folder_manager():
    return render_template("folder-manager.html", device_name=server.device_name, is_running=server.isRunning,
                           folders=server.list_folders())


@app.route("/manage-folders")
def manage_folders():
    return render_template("manage-folders.html", device_name=server.device_name, is_running=server.isRunning)


@app.route("/share-folders")
def share_folders():
    return render_template("share-folders.html", device_name=server.device_name,
                           device_to_share_name=server.device_name_to_share, is_running=server.isRunning,
                           folders=server.list_folders())


@app.route("/wait-for-share")
def wait_for_share():
    server.create_server_sharing()
    return "ok", 200


@app.route("/share-folders-list")
def share_folders_list():
    args = request.args
    folders_str = args.get("list")
    folders = folders_str.split(",")[:-1]

    for folder in folders:
        server.share_folder(folder)
    return "ok", 200


@app.route("/add_folder", methods=["GET"])
def add_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    root.destroy()

    if not folder_path:  # no folder path stop
        return "ok", 200

    proceed = easygui.ccbox(f"Are you sure you want to encrypt: {folder_path}", title='Confirm path folder')

    if proceed:
        server.add_folder(folder_path)
        return "ok", 200
    else:
        return "ok", 200


@app.route('/unlock_all_folders')
def unlock_all_folders():
    server.unlock_folders()
    return "ok", 200


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
        return 'invalid path', 403

    resp = server.remove_folder(remove_path)

    if resp:
        return 'ok', 200
    else:
        return 'Error on removing', 403


@app.route('/list')
def list():
    s = ""
    for e in server.list_folders():
        s += e + "\n"
    return s, 200


@app.route('/toggle-encryption')
def toggle_encryption():
    args = request.args
    path = args.get("path")
    is_encrypted = args.get("is_encrypted")

    server.toggle_encryption(path, is_encrypted == "True")
    return "ok", 200


def run():
    if not server.isRunning:
        threading.Thread(target=server.run_server).start()


if __name__ == "__main__":
    app.run(debug=True)
