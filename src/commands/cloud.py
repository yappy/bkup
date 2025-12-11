import logging
import argparse

log = logging.getLogger(__name__)


def cloud(args: argparse.Namespace):
    raise RuntimeError("Not Implemented")


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Copy the latest archive file to a cloud storage",
        epilog="This is rclone wrapper",
    )
    parser.add_argument("--src", "-s", nargs="+", help="backup source file")
    parser.add_argument("--dst", "-d", required=True, help="backup destination dir")
    parser.add_argument("--dry-run", "-n", action="store_true", help="dry run")

    args = parser.parse_args(argv[1:])

    cloud(args)
