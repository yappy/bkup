import logging
import argparse

log = logging.getLogger(__name__)


def clean(args: argparse.Namespace):
    raise RuntimeError("")


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Clean old archive files",
    )
    parser.add_argument("--dst", "-d", required=True, help="archive files dir")
    parser.add_argument("--dry_run", "-n", action="store_true", help="dry run")

    args = parser.parse_args(argv[1:])

    clean(args)
