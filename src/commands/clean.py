import logging
import argparse
import pathlib
import time
from . import util

log: logging.Logger = logging.getLogger(__name__)


def clean(args: argparse.Namespace):
    dst = pathlib.Path(args.dst)
    if not dst.is_dir():
        raise RuntimeError("<dst> must be a directory")

    keep_count = args.keep_count
    keep_days = args.keep_days
    if keep_count is None and keep_days is None:
        raise RuntimeError("At least one condition is needed")

    # filter children by FILE (not dir) and name_filter
    it = filter(lambda p: p.is_file(), dst.iterdir())
    it = filter(util.name_filter, it)
    # path => (mtime, path)
    files = list(map(lambda p: (p.stat().st_mtime, p), it))
    # sort by mtime (newer one will be processed earlier)
    files.sort(reverse=True)

    now = time.time()
    for i, (mtime, path) in enumerate(files):
        keep = False
        if keep_count is not None:
            if i < keep_count:
                log.info(f"Keep by count ({i + 1}): {str(path)}")
                keep = True
        if keep_days is not None:
            # UNIX time (sec) => (day: float)
            t = (now - mtime) / (24 * 60 * 60)
            if t <= keep_days:
                log.info(f"Keep by days ({int(t)}): {str(path)}")
                keep = True

        if not keep:
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
    parser.add_argument("--keep-count", type=int, help="keep the latest N files")
    parser.add_argument("--keep-days", type=int, help="keep files not expired")

    args = parser.parse_args(argv[1:])

    clean(args)
