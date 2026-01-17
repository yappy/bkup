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
import datetime
from . import util

log: logging.Logger = logging.getLogger(__name__)


def cloud(args: argparse.Namespace):
    dry_run = args.dry_run
    keep_count = args.keep_count
    keep_days = args.keep_days
    if keep_count is None and keep_days is None:
        raise RuntimeError("At least one condition is needed")

    # print total/used/free
    util.exec(["rclone", "about", f"{args.remote}:"])
    # mkdir if dst doen't exist
    # dirpath "" causes SEGV
    if args.dst != "":
        util.exec(["rclone", "mkdir", f"{args.remote}:{args.dst}"], dry_run=dry_run)

    # lsjson and filter
    stdout = util.exec_out(["rclone", "lsjson", f"{args.remote}:{args.dst}"])
    lsresult = json.loads(stdout)
    print(f"Received {len(lsresult)} files")
    lsresult = list(filter(lambda e: not e["IsDir"] and util.name_filter_str(e["Name"]), lsresult))
    print(f"{len(lsresult)} archive files")
    # convert ISO datetime str
    for entry in lsresult:
        entry["ModTime"] = datetime.datetime.fromisoformat(entry["ModTime"])
    lsresult.sort(key=lambda e: e["ModTime"], reverse=True)

    for i, entry in enumerate(lsresult):
        print(i, entry)


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
