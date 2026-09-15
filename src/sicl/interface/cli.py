from __future__ import annotations

from ..cli import CLI


def main() -> None:
    cli = CLI()
    while not cli.closed:
        try:
            command = input("sicl> ")
        except EOFError:
            break
        print(cli.execute(command))
