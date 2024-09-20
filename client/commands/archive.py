import logging
import argparse
import pathlib
import subprocess
import platform
import getpass
import datetime
from . import simpletoml

log = logging.getLogger(__name__)

CMD_UNIX = "tar"
CMD_WIN = "tar.exe"
EXT = "tar.bz2"
TAR_OPTS = ["--use-compress-prog=pbzip2"]

def exec(cmd: list[str], dry_run: bool):
    log.info(f"EXEC: {' '.join(cmd)}")
    if not dry_run:
        subprocess.run(cmd, check=True)
    else:
        log.info("dry_run")

def is_win():
    system = platform.system()
    return system == "Windows"

def archive_unix_bz2(src: pathlib.Path, ar_dst: pathlib.Path, dry_run: bool):
    try:
        # -C: change to directory DIR
        # -c: Create new.
        # -f: Specify file name.
        cmd = ["tar", "-C", str(src), "-cf", str(ar_dst)] + TAR_OPTS + ["."]
        exec(cmd, dry_run)
    except:
        ar_dst.unlink(missing_ok=True)
        raise

def archive(args: argparse.Namespace):
    # get user@host and datetime for archive file name
    user = getpass.getuser()
    host = platform.node()
    dt_now = datetime.datetime.now()
    dt_str = dt_now.strftime('%Y%m%d%H%M')

    # ensure SRC is dir and mkdir DST
    src = pathlib.Path(args.src).expanduser().resolve()
    if not src.is_dir():
        raise RuntimeError("SRC must be a directory")
    dst = pathlib.Path(args.dst).expanduser().resolve()
    dst.mkdir(parents=True, exist_ok=True)
    if not dst.is_dir():
        raise RuntimeError("DST must be a directory")
    log.info(f"mkdir: {dst}")
    ar_dst = dst / f"{user}_{host}_{dt_str}.{EXT}"
    log.info(f"SRC: {src}")
    log.info(f"DST: {ar_dst}")

    if is_win():
        pass
    else:
        archive_unix_bz2(src, ar_dst, args.dry_run)

    log.info(f"OK: {ar_dst}")

def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog = argv[0],
        description="Archive and compress directory",
    )
    parser.add_argument("--src", default="", help="backup source dir")
    parser.add_argument("--dst", default="", help="backup destination dir")
    parser.add_argument("--exclude-dir", default=[], action="append", help="exclude dir pattern")
    parser.add_argument("--dry_run", "-d", action="store_true", help="dry run")
    parser.add_argument("--print-toml", action="store_true", help="output TOML file with default parameters")
    parser.add_argument("--toml", default="", help="read paratemers from TOML")

    args = simpletoml.parse_with_toml(parser, argv[1:])

    if not args.src or not args.dst:
        parser.print_help()
        print()
        raise RuntimeError("SRC and DST are required")

    archive(args)
