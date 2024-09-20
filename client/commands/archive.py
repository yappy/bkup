import logging
import argparse
import pathlib
import tempfile
import shutil
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

def unix_main(args: argparse.Namespace):
    log.info("archive for linux")

    # get user@host and datetime for archive file name
    user = getpass.getuser()
    host = platform.node()
    dt_now = datetime.datetime.now()
    dt_str = dt_now.strftime('%Y%m%d%H%M')

    if not args.src or not args.dst:
        raise RuntimeError("SRC and DST are required")
    src = pathlib.Path(args.src).expanduser().resolve()
    if not src.is_dir():
        raise RuntimeError("SRC must be a directory")
    dst = pathlib.Path(args.dst).expanduser().resolve()
    dst.mkdir(parents=True, exist_ok=True)
    log.info(f"mkdir: {dst}")
    ar_dst = dst / f"{user}_{host}_{dt_str}.{EXT}"
    log.info(f"SRC: {src}")
    log.info(f"DST: {ar_dst}")

    with tempfile.NamedTemporaryFile(suffix=f".{EXT}") as tf:
        log.info(f"temp file created: {tf.name}")
        # -C: change to directory DIR
        # -a: Use archive suffix to determine the compression program.
        # -c: Create new.
        # -f: Specify file name.
        cmd = ["tar", "-C", str(src), "-acf", tf.name] + TAR_OPTS + ["."]
        exec(cmd, args.dry_run)

        log.info(f"copy {tf.name} -> {ar_dst}")
        shutil.copyfile(tf.name, str(ar_dst))
        log.info(f"delete temp file: {tf.name}")
        # close and delete
    log.info(f"OK: {ar_dst}")

def win_main():
    log.info("archive for windows")
    assert False, "Not implemented"

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

    system = platform.system()
    if system == "Windows":
        win_main()
    else:
        unix_main(args)
