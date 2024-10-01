import logging
import argparse
import pathlib
import time
import re

log = logging.getLogger(__name__)

DEFAULT_KEEP_COUNT = 5
DEFAULT_KEEP_DAYS = 90
# [not-num*]YYYYMMDD[num*]
PAT = re.compile(r"^.*\D(\d{8,})$")
EXTS = {
    "tar.gz",
    "tar.bz2",
    "tar.xz",
    "zip",
    "7z",
}


def name_filter(path: pathlib.Path) -> bool:
    tokens = path.name.split(".", maxsplit=1)
    if len(tokens) < 2:
        return False
    noext, ext = tokens

    if ext not in EXTS:
        return False

    m = PAT.match(noext)

    return bool(m)


def clean(args: argparse.Namespace):
    dst = pathlib.Path(args.dst)
    if not dst.is_dir():
        raise RuntimeError("<dst> must be a directory")

    # filter children by FILE (not dir) and name_filter
    it = filter(lambda p: p.is_file(), dst.iterdir())
    it = filter(name_filter, it)
    # path => (mtime, path)
    files = list(map(lambda p: (p.stat().st_mtime, p), it))
    # sort by mtime (newer one will be processed earlier)
    files.sort(reverse=True)

    keep_count = args.keep_count
    keep_days = args.keep_days
    now = time.time()
    for i, (mtime, path) in enumerate(files):
        if i < keep_count:
            log.info(f"Keep by count ({i + 1}): {str(path)}")
            continue
        # UNIX time (sec) => (day: float)
        t = (now - mtime) / (24 * 60 * 60)
        if t <= keep_days:
            log.info(f"Keep by days ({int(t)}): {str(path)}")
            continue

        log.info(f"delete: {str(path)}")
        if args.dry_run:
            log.info("(dry run)")
        path.unlink()

    log.info("OK")


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Clean old archive files",
        epilog="A file will be deleted only if it is out of --keep-count AND out of --keep-days"
    )
    parser.add_argument("--dst", "-d", required=True, help="archive files dir")
    parser.add_argument("--dry_run", "-n", action="store_true", help="dry run")
    parser.add_argument("--keep-count", type=int, default=DEFAULT_KEEP_COUNT, help="keep the latest N files")
    parser.add_argument("--keep-days", type=int, default=DEFAULT_KEEP_DAYS, help="keep files not expired")

    args = parser.parse_args(argv[1:])

    clean(args)
