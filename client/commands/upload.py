import logging
import argparse
import pathlib

log = logging.getLogger(__name__)


def upload(args: argparse.Namespace):
    src = pathlib.Path(args.src)
    latest = src / "latest.txt"

    log.info(f"Read the latest archive: {str(latest)}")
    with latest.open() as fin:
        latest_file = src / fin.readline().strip()
    log.info(f"The latest archive: {str(latest_file)}")
    if not latest_file.is_file():
        raise RuntimeError(f"{str(latest_file)} is not a valid file")

    cmd = [
        "rsync",
        # archive mode (=-rlptgoD), compress, skip if dst is newer
        "-azu",
    ]


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Archive and compress a directory (Linux: tar.bz2, Windows: 7z)",
    )
    parser.add_argument("--src", "-s", required=True, help="archive dir")
    parser.add_argument("--dst", "-s", required=True, help="rsync destination (user@host:dir)")
    parser.add_argument("--dry-run", "-n", action="store_true", help="dry run")

    args = parser.parse_args(argv[1:])

    upload(args)
