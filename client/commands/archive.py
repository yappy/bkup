import argparse
import platform
import tomllib
from . import simpletoml

def unix_main():
    assert False, "Not implemented"

def win_main():
    assert False, "Not implemented"

def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog = argv[0],
        description="Archive and compress directory",
    )
    parser.add_argument("--src", default="", help="backup source dir")
    parser.add_argument("--dst", default="", help="backup destination dir")
    parser.add_argument("--exclude-dir", default=[], action="append", help="exclude dir pattern")
    parser.add_argument("--dry_run", "-d", action="store_true", help="dry run")
    parser.add_argument("--print-toml", action="store_true", help="output TOML file with default parameters")
    parser.add_argument("--toml", default="", help="read paratemers from TOML")

    args = simpletoml.parse_with_toml(parser, argv[1:])

    system = platform.system()
    if system == "Windows":
        win_main()
    else:
        unix_main()
