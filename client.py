from bluetooth import *

# Create the client socket


client_socket = BluetoothSocket(RFCOMM)

client_socket.connect(("7C:B0:C2:4F:4F:F6", PORT_ANY))

client_socket.send("Hello World")

client_socket.close()

print("Finished")
