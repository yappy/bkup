import logging
import argparse
import pathlib
import subprocess
import os
import platform
import getpass
import datetime

log = logging.getLogger(__name__)

CMD_UNIX = "tar"
CMD_WIN = "%ProgramFiles%\\7-Zip\\7z.exe"
EXT_UNIX = "tar.bz2"
EXT_WIN = "7z"
TAR_OPTS = ["--use-compress-prog=pbzip2"]

def exec(cmd: list[str], dry_run: bool):
    log.info(f"EXEC: {' '.join(cmd)}")
    if not dry_run:
        subprocess.run(cmd, check=True)
    else:
        log.info("dry_run")

def archive_unix_bz2(src: pathlib.Path, ar_dst: pathlib.Path, dry_run: bool):
    try:
        # -C: change to directory DIR
        # -c: Create new.
        # -f: Specify file name.
        cmd = ["tar", "-C", str(src), "-cf", str(ar_dst)] + TAR_OPTS + ["."]
        exec(cmd, dry_run)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            # Warning (Non fatal error(s)).
            log.warning("tar exit with warning(s)")
        else:
            raise
    except:
        log.error("Exec tar with pbzip2 error.")
        log.error("[Hint] Did you install pbzip2 (parallel bzip2)?")
        log.error("e.g. $ sudo apt install pbzip2")
        ar_dst.unlink(missing_ok=True)
        raise

def archive_win_7z(src: pathlib.Path, ar_dst: pathlib.Path, dry_run: bool):
    prog = os.path.expandvars(CMD_WIN)
    try:
        cmd = [prog, "a", str(ar_dst), str(src)]
        exec(cmd, dry_run)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            # Warning (Non fatal error(s)).
            log.warning("7z exit with warning(s)")
        else:
            raise
    except:
        log.error("Exec 7z error.")
        log.error("[Hint] Did you install 7z?")
        log.error("e.g. $ winget install 7zip")
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
    log.info(f"SRC: {src}")

    if platform.system() == "Windows":
        ar_dst = dst / f"{user}_{host}_{dt_str}.{EXT_WIN}"
        log.info(f"DST: {ar_dst}")
        archive_win_7z(src, ar_dst, args.dry_run)
    else:
        ar_dst = dst / f"{user}_{host}_{dt_str}.{EXT_UNIX}"
        log.info(f"DST: {ar_dst}")
        archive_unix_bz2(src, ar_dst, args.dry_run)

    log.info(f"OK: {ar_dst}")

def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog = argv[0],
        description="Archive and compress a directory (Linux: tar.bz2, Windows: 7z)",
    )
    parser.add_argument("--src", "-s", required=True, help="backup source dir")
    parser.add_argument("--dst", "-d", required=True, help="backup destination dir")
    parser.add_argument("--dry_run", "-n", action="store_true", help="dry run")

    args = parser.parse_args(argv[1:])

    archive(args)
