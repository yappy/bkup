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


def ls(remote: str, dst: str):
    stdout = util.exec_out(["rclone", "lsjson", f"{remote}:{dst}"])
    return json.loads(stdout)


def cloud(args: argparse.Namespace):
    dry_run = args.dry_run

    # print total/used/free
    util.exec(["rclone", "about", f"{args.remote}:"])
    # mkdir if dst doen't exist
    # dirpath "" causes SEGV
    if args.dst != "":
        util.exec(["rclone", "mkdir", f"{args.remote}:{args.dst}"], dry_run=dry_run)

    lsresult = ls(args.remote, args.dst)
    it = map(lambda fobj: fobj['Name'], lsresult)
    it = filter(util.name_filter_str, it)
    for entry in it:
        print(entry)


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Copy the latest archive file to a cloud storage",
        epilog="This is rclone wrapper",
    )
    parser.add_argument("--remote", "-r", required=True, help="backup destination remote name")
    parser.add_argument("--dst", "-d", default="", help="backup destination dir on remote (remote:HERE)")
    parser.add_argument("--dry-run", "-n", action="store_true", help="dry run")
    parser.add_argument("--keep-count", type=int, help="keep the latest N files")
    parser.add_argument("--keep-days", type=int, help="keep files not expired")

    args = parser.parse_args(argv[1:])

    cloud(args)
