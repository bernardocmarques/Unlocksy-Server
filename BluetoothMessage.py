import base64
from datetime import datetime, timedelta

import Crypto.Random


class BluetoothMessage:

    def __init__(self, message, nonce=None, t1=None, t2=None):
        self.message = message

        if nonce and t1 and t2:
            self.nonce = base64.b64encode(Crypto.Random.get_random_bytes(16)).decode()
            self.t1 = datetime.fromtimestamp(t1)
            self.t2 = datetime.fromtimestamp(t2)
        else:
            self.nonce = base64.b64encode(Crypto.Random.get_random_bytes(16)).decode()
            now = datetime.now()
            self.t1 = now - timedelta(seconds=30)
            self.t2 = now + timedelta(seconds=30)

    def __str__(self):
        print(datetime.now())
        return self.message + "," + self.nonce + "," + str(int(self.t1.timestamp() * 1000)) + "," + str(int(self.t2.timestamp() * 1000)) + ""
