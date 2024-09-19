import argparse
import platform
import tomllib
from . import simpletoml

def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog = argv[0],
        description="Archive and compress directory",
    )
    parser.add_argument("--src", default="", help="backup source dir")
    parser.add_argument("--dst", default="", help="backup destination dir")
    parser.add_argument("--exclude-dir", default=[], action="append", help="exclude dir pattern")
    parser.add_argument("--dry_run", "-d", action="store_true", help="dry run")
    parser.add_argument("--print-toml", action="store_true", help="output toml file with default parameters")

    args = parser.parse_args(argv[1:])

    if args.print_toml:
        toml = f"# {argv[0]} - {parser.description}\n"
        defs = parser.parse_args([])
        toml += simpletoml.as_toml(vars(defs))
        print(toml, end="")
