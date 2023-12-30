import argparse
import socket
import subprocess
import time
from typing import Optional


def spawn_gnugo_server(host: str, port: int) -> subprocess.Popen:
    proc = subprocess.Popen(
        "gnugo --mode gtp --gtp-listen {}:{}".format(host, port),
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    print("Spawn gnugo(pid:{}) lsiten at {}:{}".format(proc.pid, host, port))
    time.sleep(2)
    return proc


def spawn_gnugo_client(host: str, port: int) -> subprocess.Popen:
    proc = subprocess.Popen(
        "gnugo --mode gtp --gtp-connect {}:{}".format(host, port),
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    print("Spawn gnugo(pid:{}) connect to {}:{}".format(proc.pid, host, port))
    time.sleep(2)
    return proc


def gtp_client(host: str, port: int) -> socket.SocketType:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (host, port)
    print("connecting to {} port {}".format(*server_address))
    sock.connect(server_address)
    return sock


def gtp_server(host: str, port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    address = (host, port)
    print("listening to {} port {}".format(*address))
    sock.bind(address)
    sock.listen(1)
    return sock


def send_command(connection, command: bytes) -> bytearray:
    connection.send(command)

    data = bytearray()

    while True:
        if command == b"quit\n":
            print("quit")
            connection.close()
            break
        data.extend(connection.recv(4096))
        if len(data) == 0 or data[-2:] == b"\n\n":
            break
    return data


def client(host: str, port: int):
    spawn_gnugo_server(host, port)
    gtp = gtp_client(host, port)
    try:
        while True:
            # Send data
            message = bytes("{}\n".format(input("> ")), "utf-8")
            print("sending {!r}".format(message))
            data = send_command(gtp, message)

            if data:
                print("received {} bytes\n {}".format(len(data), str(data, "utf-8")))
            else:
                raise

    except Exception as e:
        print("closing socket because: {!r}".format(e))
    except KeyboardInterrupt as e:
        print(e)
    finally:
        gtp.close()


def handle_client(
    client: socket.SocketType, addr: str, command: bytes
) -> Optional[bytearray]:
    try:
        # Send data
        print("sending {!r}".format(command))
        data = send_command(client, command)

        if data:
            return data
    except Exception as e:
        print("connection form {} ended because {}".format(addr, e))
        client.close()
    return None


def parse_move_result(input: bytearray) -> str:
    return input.strip(b"= \n\t").decode("utf-8")


def play(clients):
    color, vertex = None, None
    i = 0
    pass_cnt = 0

    while True:
        # time.sleep(0.1)
        (client, addr) = clients[i % 2]
        i += 1
        if color is None and vertex is None:
            # move first time
            command = bytes("genmove b\n", "utf-8")
            color = "black"
            move_result = handle_client(client, addr, command)
        else:
            command = bytes("play {} {}\n".format(color, vertex), "utf-8")
            if handle_client(client, addr, command) is None:
                print("client {} sends no data".format(client))
                break
            if color == "black":
                command = bytes("genmove w\n", "utf-8")
                color = "white"
            else:
                command = bytes("genmove b\n", "utf-8")
                color = "black"
            move_result = handle_client(client, addr, command)
        if move_result is not None:
            vertex = parse_move_result(move_result)
            if vertex == "PASS":
                pass_cnt += 1
            else:
                pass_cnt = 0
        else:
            print("client {} sends no data".format(client))
            break
        if pass_cnt == 2:
            data = handle_client(client, addr, b"showboard\n")
            if data is None:
                break
            print(str(data, "utf-8"))
            data = handle_client(client, addr, b"final_score\n")
            if data is None:
                break
            print("score: {}".format(str(data, "utf-8")))
            break


def server(host: str, port: int):
    gtp = gtp_server(host, port)
    spawn_gnugo_client(host, port)
    spawn_gnugo_client(host, port)
    clients = []
    while len(clients) != 2:
        # Wait for a connection
        client, addr = gtp.accept()
        print("connection from", addr)
        clients.append((client, addr))

    play(clients)
    gtp.close()


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
        metavar="{1..65535}",
    )
    parser.add_argument(
        "-m",
        dest="mode",
        choices=["client", "server"],
        default="server",
    )
    args = parser.parse_args()

    host = args.host
    port = args.port

    if args.mode == "client":
        client(host, port)
    elif args.mode == "server":
        server(host, port)


if __name__ == "__main__":
    main()
