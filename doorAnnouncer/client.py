import socket

host_ip, server_port = "192.168.0.133", 9999
data = " Hello how are you?\n"

# Initialize a TCP client socket using SOCK_STREAM
tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Establish connection to TCP server and exchange data
    tcp_client.connect((host_ip, server_port))
    tcp_client.sendall(data.encode())

    # Read data from the TCP server and close the connection
    received = tcp_client.recv(1024)
finally:
    tcp_client.close()

print("Bytes Sent:     {}".format(data))
print("Bytes Received: {}".format(received.decode()))


# if command == 'update':
#     self.request.sendall(json.dumps({
#         'doorOpen': doorOpen,
#         'clips': clips
#     }).encode())
# elif command == 'toggle door':
#     doorOpen = not doorOpen
# elif command == 'door closed':
#     doorOpen = False
# elif command == 'door open':
#     doorOpen = True
# # Told to play one of the clips
# elif command in files:
#     playClip(join(CLIP_DIR, command))
# elif len(command) > MINIMUM_AUDIO_CLIP_SIZE + 10 and command.startswith('clip'):
#     name = re.match('clip (.+wav) ', self.data)
#     if name is None:
#         print("invalid sound data:")
#         print(self.data)
#     else:
#         name = name.groups()[0]
