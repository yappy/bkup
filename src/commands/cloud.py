# Sample
# {
# 'Path': 'Getting started with pCloud.pdf',
# 'Name': 'Getting started with pCloud.pdf',
# 'Size': 16371465,
# 'MimeType': 'application/pdf',
# 'ModTime':
# '2024-04-07T15:16:05Z',
# 'IsDir': False,
# 'ID': 'f42732115267'
# }

import logging
import argparse
import pathlib
from . import util

log: logging.Logger = logging.getLogger(__name__)


def cloud(args: argparse.Namespace):
    src = pathlib.Path(args.src)
    dst = f"{args.remote}:{args.dst}"
    latest = src / "latest.txt"

    log.info(f"Read the latest archive: {str(latest)}")
    with latest.open() as fin:
        latest_file = src / fin.readline().strip()
    log.info(f"The latest archive: {str(latest_file)}")
    if not latest_file.is_file():
        raise RuntimeError(f"{str(latest_file)} is not a valid file")

    dry_run = args.dry_run
    # print total/used/free
    util.exec(["rclone", "about", f"{args.remote}:"], dry_run=dry_run)
    # mkdir if dst doen't exist
    # dirpath "" causes SEGV
    if args.dst != "":
        cmd = ["rclone", "mkdir", dst]
        if dry_run:
            cmd += ["-n"]
        util.exec(cmd)

    cmd = ["rclone", "copy", str(latest_file), dst]
    if args.progress:
        cmd += ["-P"]
    if dry_run:
        cmd += ["-n"]

    util.exec(cmd)
    log.info("OK")


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Copy the latest archive file to a cloud storage",
        epilog="This is rclone wrapper",
    )
    parser.add_argument("--src", "-s", required=True, help="archive dir")
    parser.add_argument("--remote", "-r", required=True, help="backup destination remote name")
    parser.add_argument("--dst", "-d", default="", help="backup destination dir on remote (remote:HERE)")
    parser.add_argument("--progress", "-P", action="store_true", help="show progress")
    parser.add_argument("--dry-run", "-n", action="store_true", help="dry run")

    args = parser.parse_args(argv[1:])

    cloud(args)
