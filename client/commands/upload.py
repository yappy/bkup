import logging
import argparse

log = logging.getLogger(__name__)


def upload(args: argparse.Namespace):
    raise RuntimeError("")


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Archive and compress a directory (Linux: tar.bz2, Windows: 7z)",
    )
    parser.add_argument("--src", "-s", required=True, help="backup source dir")
    parser.add_argument("--dry_run", "-n", action="store_true", help="dry run")

    args = parser.parse_args(argv[1:])

    upload(args)
