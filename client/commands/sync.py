import logging
import argparse
import pathlib
import subprocess
import multiprocessing
import os
import platform

log = logging.getLogger(__name__)

def robocopy(src_list: list[pathlib.Path], dst: pathlib.Path, exclude_file: list[str], exclude_dir: list[str], dry_run: bool, force: bool):
    for src in src_list:
        robocopy_one(src, dst, exclude_file, exclude_dir, dry_run, force)

# dir sync for windows
def robocopy_one(src: pathlib.Path, dst: pathlib.Path, exclude_file: list[str], exclude_dir: list[str], dry_run: bool, force: bool):
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
    if exclude_file:
        cmd += ["/XF"]
        cmd += exclude_file
    if exclude_dir:
        cmd += ["/XD"]
        cmd += exclude_dir
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

    proc = subprocess.run(cmd, check=False)
    log.info(f"Robocopy returned: {proc.returncode}")
    if proc.returncode >= 8:
        raise RuntimeError(f"Robocopy returned: {proc.returncode}")

def rsync(src_list: list[pathlib.Path], dst: pathlib.Path, exclude: list[str], dry_run: bool, force: bool):
    # command and -param
    cmd = [
        "rsync",
        # archive mode (=-rlptgoD)
        "-a"
    ]
    # SRC and DST are checked by 'required' option in parse.
    # But check again because rsync dst will be destroyed ant it is dangerous.
    assert type(src_list) is list and all((isinstance(src, os.PathLike) for src in src_list))
    assert isinstance(dst, os.PathLike)
    # SRC...
    cmd.extend(map(str, src_list))
    # DST
    cmd.append(str(dst))

    print(cmd)

def sync(args: argparse.Namespace):
    # ensure SRC is dir and mkdir DST
    def expand_and_check(src):
        p = pathlib.Path(src).expanduser().resolve()
        if not p.is_dir():
            raise RuntimeError("SRC must be a directory")
        return p
    src_list = list(map(expand_and_check , args.src))
    dst = pathlib.Path(args.dst).expanduser().resolve()
    log.info(f"mkdir: {dst}")
    dst.mkdir(parents=True, exist_ok=True)
    if not dst.is_dir():
        raise RuntimeError("DST must be a directory")
    log.info(f"SRC: {src_list}")
    log.info(f"DST: {dst}")

    if any(map(lambda src: dst.is_relative_to(src), src_list)):
        raise RuntimeError(f"one of src_list is parent of {dst}")

    if platform.system() == "Windows":
        if args.exclude:
            raise RuntimeError("--exclude is unavailable for Robocopy")
        robocopy(src_list, dst, args.exclude_file, args.exclude_dir, args.dry_run, args.force)
    else:
        if args.exclude_file or args.exclude_dir:
            raise RuntimeError("--exclude-file and --exclude-dir are unavailable for rsync")
        rsync(src_list, dst, args.exclude, args.dry_run, args.force)

    log.info(f"OK")

def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog = argv[0],
        description="Make a copy of file tree (Linux: rsync, Windows: robocopy)",
        epilog="Make sure of what will happen because sync operation may destruct the dest dir.",
    )
    parser.add_argument("--src", required=True, default=[], action="append", help="backup source dir (multiple OK)")
    parser.add_argument("--dst", required=True, help="backup destination dir")
    parser.add_argument("--exclude", "-x", action="append", default=[], help="exclude pattern (rsync)")
    parser.add_argument("--exclude-file", "-xf", action="append", default=[], help="exclude file (Robocopy)")
    parser.add_argument("--exclude-dir", "-xd", action="append", default=[], help="exclude dir (Robocopy)")
    parser.add_argument("--dry_run", "-d", action="store_true", help="dry run")
    parser.add_argument("--force", "-f", action="store_true", help="run without confirmation")

    try:
        args = parser.parse_args(argv[1:])
    except:
        parser.print_help()
        raise

    sync(args)
