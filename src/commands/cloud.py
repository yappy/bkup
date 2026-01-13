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
import json
from . import util

log: logging.Logger = logging.getLogger(__name__)


def ls(remote: str, dst: str, dry_run: bool):
    stdout = util.exec_out(["rclone", "lsjson", f"{remote}:{dst}"], dry_run=dry_run)
    obj = json.loads(stdout)
    print(obj)


def cloud(args: argparse.Namespace):
    dry_run = args.dry_run
    # print total/used/free
    util.exec(["rclone", "about", f"{args.remote}:"], dry_run=dry_run)
    # mkdir if dst doen't exist
    # dirpath "" causes SEGV
    if args.dst != "":
        util.exec(["rclone", "mkdir", f"{args.remote}:{args.dst}"], dry_run=dry_run)

    ls(args.remote, args.dst, dry_run)

    raise RuntimeError("Not Implemented")


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Copy the latest archive file to a cloud storage",
        epilog="This is rclone wrapper",
    )
    parser.add_argument("--src", "-s", required=True, help="archive dir")
    parser.add_argument("--remote", "-r", required=True, help="backup destination remote name")
    parser.add_argument("--dst", "-d", default="", help="backup destination dir on remote (remote:HERE)")
    parser.add_argument("--dry-run", "-n", action="store_true", help="dry run")

    args = parser.parse_args(argv[1:])

    cloud(args)
