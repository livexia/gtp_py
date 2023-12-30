import argparse
import socket
import subprocess
import time


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
        default="127.0.0.1",
        help="Connect host, default is 127.0.0.1",
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
    # Spawn gnugo --mode gtp --gtp-listen 127.0.0.1:20231
    proc = subprocess.Popen(
        "gnugo --mode gtp --gtp-listen {}:{}".format(host, port),
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    time.sleep(2)

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (host, port)
    print("connecting to {} port {}".format(*server_address))
    sock.connect(server_address)

    try:
        while True:
            # Send data
            message = bytes("{}\n".format(input("> ")), "utf-8")
            print("sending {!r}".format(message))
            sock.send(message)

            data = bytearray()

            while True:
                if message == b"quit\n":
                    print("quit")
                    raise ConnectionResetError
                data.extend(sock.recv(4096))
                if len(data) == 0 or data[-2:] == b"\n\n":
                    break
            print("received\n {}".format(str(data, "utf-8")))

    except Exception as e:
        print("closing socket because: {!r}".format(e))
        sock.close()
    except KeyboardInterrupt as e:
        print(e)
        sock.close()


if __name__ == "__main__":
    main()
