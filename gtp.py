import argparse
import socket
import subprocess
import time
from typing import Optional


def spawn_gnugo(host: str, port: int) -> subprocess.Popen:
    proc = subprocess.Popen(
        "gnugo --mode gtp --gtp-listen {}:{}".format(host, port),
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    print("Spawn gnugo at {}:{} pid: {}".format(host, port, proc.pid))
    time.sleep(2)
    return proc


def connect_to_gtp(host: str, port: int) -> socket.SocketType:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (host, port)
    print("connecting to {} port {}".format(*server_address))
    sock.connect(server_address)
    return sock


def send_command(gtp, command: bytes) -> Optional[bytearray]:
    gtp.send(command)

    data = bytearray()

    while True:
        if command == b"quit\n":
            print("quit")
            raise ConnectionResetError
        data.extend(gtp.recv(4096))
        if len(data) == 0 or data[-2:] == b"\n\n":
            break
    return data


class PortNumber(int):
    def __init__(self, i):
        self = int(i)
        if self not in range(1, 65536):
            raise argparse.ArgumentTypeError(
                "port number must be integers between 0 and 65535"
            )


def main():
    parser = argparse.ArgumentParser(description="A wrapper for Go Text Protocol")
    parser.add_argument(
        "-a",
        dest="host",
        default=socket.gethostname(),
        help="Connect host, default is local hostname",
    )
    parser.add_argument(
        "-p",
        dest="port",
        type=PortNumber,
        required=True,
        help="Connect port",
        metavar="[1..65535]",
    )
    args = parser.parse_args()

    host = args.host
    port = args.port

    spawn_gnugo(host, port)

    gtp = connect_to_gtp(host, port)

    try:
        while True:
            # Send data
            message = bytes("{}\n".format(input("> ")), "utf-8")
            print("sending {!r}".format(message))
            data = send_command(gtp, message)

            if data is not None:
                print("received\n {}".format(str(data, "utf-8")))
            else:
                raise

    except Exception as e:
        print("closing socket because: {!r}".format(e))
        gtp.close()
    except KeyboardInterrupt as e:
        print(e)
        gtp.close()


if __name__ == "__main__":
    main()
