import argparse
import subprocess
import time
import logging
import io
import random


def append_newline(func):
    def wrapper(*args, **kwargs):
        args = list(args)
        for i, v in enumerate(args):
            if type(v) is str and not v.endswith("\n"):
                args[i] = v + "\n"
        for k, v in kwargs:
            if type(v) is str and not v.endswith("\n"):
                kwargs[k] = v + "\n"
        return func(*args, **kwargs)

    return wrapper


class Engine:
    def __init__(self, config=[]):
        self.proc = spawn_gnugo()
        self.stdin = io.TextIOWrapper(
            self.proc.stdin,
            encoding="utf-8",
            line_buffering=True,  # send data on newline
        )
        self.stdout = io.TextIOWrapper(
            self.proc.stdout,
            encoding="utf-8",
        )
        if config:
            for c in config:
                logging.info(
                    "config {!r} with command {}: {}".format(
                        self, c, self.send(c).rstrip()
                    )
                )

    def __repr__(self) -> str:
        return "Engine pid: {}".format(self.proc.pid)

    @append_newline
    def send(self, command: str) -> str:
        self.stdin.write(command)
        if command == "quit\n":
            self.close()
            return ""
        else:
            return self._read()

    def _read(self) -> str:
        data = ""
        while True:
            temp = self.stdout.readline()
            if temp == "\n":
                break
            data += temp
        return data

    def close(self):
        self.stdin.close()
        self.stdout.close()
        self.proc.kill()

    def board(self) -> str:
        return self.send("showboard")


def spawn_gnugo() -> subprocess.Popen:
    proc = subprocess.Popen(
        "gnugo --mode gtp",
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    logging.info("Spawn gnugo pid:{}".format(proc.pid))
    time.sleep(0.5)
    return proc


def play_with_engine(config):
    engine = Engine(config)
    colors = ["black", "white"]
    temp = random.randint(0, 1)
    player_color = colors[temp]
    engine_color = colors[1 - temp]
    engine_cmd = "genmove {}".format(engine_color)
    print("player play {}, engine play {}".format(player_color, engine_color))

    while True:
        command = input("> ")
        data = engine.send(command)
        if engine.stdin.closed:
            break
        if command.strip().startswith("play {}".format(player_color[0])):
            print(
                "engine play {} {}".format(
                    engine_color, parse_move_result(engine.send(engine_cmd))
                )
            )
            print(engine.board())
        else:
            print(data)


def parse_move_result(input: str) -> str:
    return input.strip("= \n\t")


def two_engine_play(engine1, engine2):
    color, vertex = None, None
    i = 0
    pass_cnt = 0
    engines = [engine1, engine2]

    while True:
        logging.debug(
            "{!r} play hand {}: {} {}".format(engines[(i - 1) % 2], i, color, vertex)
        )
        engine = engines[i % 2]
        if pass_cnt == 2:
            print(engine.board())
            data = engine.send("final_score")
            if not data:
                break
            print("score: {}".format(data))
            break

        i += 1
        if color is None and vertex is None:
            # move first time
            command = "genmove b"
            color = "black"
            move_result = engine.send(command)
        else:
            command = "play {} {}".format(color, vertex)
            move_result = engine.send(command)
            if not move_result:
                logging.error("engine {} sends no data".format(engine))
                break
            if color == "black":
                command = "genmove w"
                color = "white"
            else:
                command = "genmove b"
                color = "black"
            move_result = engine.send(command)
        if move_result is not None:
            vertex = parse_move_result(move_result)
            if vertex == "PASS":
                pass_cnt += 1
            else:
                pass_cnt = 0
        else:
            logging.error("client {} sends no data".format(engine))
            break


def main():
    parser = argparse.ArgumentParser(description="A wrapper for Go Text Protocol")
    parser.add_argument(
        "-c",
        dest="count",
        choices=[1, 2],
        type=int,
        help="GTP engine count: 1 play with engine, 2 engine play with each other",
    )
    parser.add_argument(
        "--boardsize",
        dest="boardsize",
        type=int,
        choices=range(9, 20),
        default=19,
        help="size of board",
    )
    parser.add_argument(
        "-v", dest="verbose", action="store_true", default=False, help="verbose output"
    )
    args = parser.parse_args()

    verbose = args.verbose

    if not verbose:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(level=level)

    engine_count = args.count
    config = ["boardsize {}".format(args.boardsize)]

    if engine_count == 1:
        play_with_engine(config)
    elif engine_count == 2:
        engine1 = Engine(config)
        engine2 = Engine(config)
        two_engine_play(engine1, engine2)


if __name__ == "__main__":
    main()
