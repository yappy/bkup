import logging
import argparse
import pathlib
import subprocess
import multiprocessing
import platform
import datetime

log = logging.getLogger(__name__)

# dir sync for windows
def robocopy(src: pathlib.Path, dst: pathlib.Path, dt_str: str, dry_run: bool, force: bool):
    log_file = dst.parent / f"robocopy_{dt_str}.txt"
    nproc = max(multiprocessing.cpu_count(), 128)
    cmd = [
        "Robocopy.exe", str(src), str(dst),
        # No progress
        "/NP",
        # Mirror (files may be deleted!)
        "/MIR",
        # Copy file and dir timestamp
        "/COPY:DAT",
        "/DCOPY:DAT",
        # Exclude System, Hidden, Temp, Offline
        # Exclude link/junction
        "/XA:SHTO",
        "/XJ",
        # Multi-threading
        f"/MT:{nproc}",
        # Retry count and Wait sec
        "/R:1",
        "/W:0 ",
    ]
    if dry_run:
        cmd += ["/L"]

    if not force:
        # + /QUIT
        subprocess.run(cmd + ["/QUIT"], check=True)
        log.warning("Caution!")
        log.warning("Mirror (/MIR) option may destruct the destination dir.")
        log.warning("(You can skip this by --force option for automation)")
        log.warning("OK? (y/N)")
        ans = input()
        if ans != "y" and ans != "Y":
            return

    # + /LOG
    proc = subprocess.run(cmd + [f"/LOG:{log_file}"], check=False)
    log.info(f"Robocopy returned: {proc.returncode}")
    if proc.returncode >= 8:
        raise RuntimeError(f"Robocopy returned: {proc.returncode}")

def sync(args: argparse.Namespace):
    dt_now = datetime.datetime.now()
    dt_str = dt_now.strftime('%Y%m%d%H%M')

    # ensure SRC is dir and mkdir DST
    src = pathlib.Path(args.src).expanduser().resolve()
    if not src.is_dir():
        raise RuntimeError("SRC must be a directory")
    dst = pathlib.Path(args.dst).expanduser().resolve()
    log.info(f"mkdir: {dst}")
    dst.mkdir(parents=True, exist_ok=True)
    if not dst.is_dir():
        raise RuntimeError("DST must be a directory")
    log.info(f"SRC: {src}")
    log.info(f"DST: {dst}")

    if dst.is_relative_to(src):
        raise RuntimeError(f"{src} is parent of {dst}")

    if platform.system() == "Windows":
        robocopy(src, dst, dt_str, args.dry_run, args.force)
    else:
        raise RuntimeError(f"not implemented")

    log.info(f"OK")

def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog = argv[0],
        description="Make a copy of file tree",
    )
    parser.add_argument("--src", default="", help="backup source dir")
    parser.add_argument("--dst", default="", help="backup destination dir")
    parser.add_argument("--dry_run", "-d", action="store_true", help="dry run")
    parser.add_argument("--force", "-f", action="store_true", help="run without confirmation")

    args = parser.parse_args(argv[1:])

    if not args.src or not args.dst:
        parser.print_help()
        print()
        raise RuntimeError("SRC and DST are required")

    sync(args)
