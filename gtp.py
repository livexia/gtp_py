import socket
import subprocess
import time

host = '127.0.0.1'
port = 20230
# Spawn gnugo --mode gtp --gtp-listen 127.0.0.1:20231 
proc = subprocess.Popen(
    'gnugo --mode gtp --gtp-listen {}:{}'.format(host, port),
    shell=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
)

time.sleep(2)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (host, port)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

try:
    while True:
        # Send data
        message = bytes("{}\n".format(input('> ')), 'utf-8')
        print('sending {!r}'.format(message))
        sock.send(message)
    
        data = bytearray()
    
        while True:
            data.extend(sock.recv(4096))
            if len(data) == 0 or data[-2:] == b'\n\n':
                break
            if message == b'quit\n':
                print("quit")
                raise ConnectionResetError
            print('received\n {}'.format(str(data, 'utf-8')))

except Exception as e:
    print('closing socket because: {!r}'.format(e))
    sock.close()
