import logging
import argparse
import pathlib
import subprocess
import multiprocessing
import os
from . import util

log = logging.getLogger(__name__)


def sync_win_robocopy(
        src_list: list[str], dst: pathlib.Path,
        exclude_file: list[str], exclude_dir: list[str],
        dry_run: bool, force: bool):
    assert src_list
    for src in src_list:
        srcpath = pathlib.PureWindowsPath(src)
        dstdir = dst / srcpath.name
        robocopy_one(src, dstdir, exclude_file, exclude_dir, dry_run, force)


# dir sync for windows
def robocopy_one(
        src: str, dst: pathlib.Path, exclude_file: list[str],
        exclude_dir: list[str], dry_run: bool, force: bool):
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
        cmd.append("/L")

    if not force:
        # + /QUIT
        subprocess.run(cmd + ["/QUIT"], check=True)
        log.warning("Caution!")
        log.warning("Mirror (/MIR) option may destruct the destination dir.")
        log.warning("(You can skip this by --force option for automation)")
        log.warning("OK? (y/N)")
        ans = input()
        if ans != "y" and ans != "Y":
            log.info("Cancelled")
            raise RuntimeError("Cancelled")

    log.info(f"EXEC: {' '.join(cmd)}")
    proc = subprocess.run(cmd, check=False)
    if proc.returncode >= 8:
        log.warning(f"Robocopy returned: {proc.returncode}")
    else:
        log.info(f"Robocopy returned: {proc.returncode}")


def sync_unix_rsync(src_list: list[str], dst: pathlib.Path, exclude: list[str], exclude_from: list[str], dry_run: bool, force: bool):
    # command and -param
    cmd = [
        "rsync",
        # archive mode (=-rlptgoD), verbose
        "-av",
        # sync (delete if src does not contain)
        "--delete",
    ]
    for pattern in exclude:
        cmd.append(f"--exclude={pattern}")
    for file in exclude_from:
        cmd.append(f"--exclude-from={file}")
    if dry_run:
        cmd.append("-n")
    # SRC and DST are checked by 'required' option in parse.
    # But check again because rsync dst will be destroyed ant it is dangerous.
    assert type(src_list) is list and all((isinstance(src, str) for src in src_list))
    assert isinstance(dst, os.PathLike)
    # SRC...
    cmd.extend(map(str, src_list))
    # DST
    cmd.append(str(dst))

    print(cmd)
    if not force and not dry_run:
        log.warning("Caution!")
        log.warning("--delete option may destruct the destination dir.")
        log.warning("(You can skip this by --force option for automation)")
        log.warning("OK? (y/N)")
        ans = input()
        if ans != "y" and ans != "Y":
            log.info("Cancelled")
            raise RuntimeError("Cancelled")

    log.info(f"EXEC: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def sync(args: argparse.Namespace):
    iswin = util.is_win()

    # ensure SRC is dir and mkdir DST
    def expand_and_check(src: str):
        add_slash = src != "/" and src.endswith("/")
        p = pathlib.Path(src).expanduser().resolve()
        if not p.is_dir():
            raise RuntimeError("SRC must be a directory")
        if add_slash:
            return str(p) + "/"
        else:
            return str(p)

    src_list = list(map(expand_and_check, args.src))
    dst = pathlib.Path(args.dst).expanduser().resolve()
    log.info(f"mkdir: {dst}")
    dst.mkdir(parents=True, exist_ok=True)
    if not dst.is_dir():
        raise RuntimeError("DST must be a directory")
    log.info(f"SRC: {src_list}")
    log.info(f"DST: {dst}")

    if any(map(lambda src: dst.is_relative_to(src), src_list)):
        raise RuntimeError(f"one of src_list is parent of {dst}")

    exe_from_wsl = False
    if util.is_wsl():
        winsrc_list = list(map(util.to_winpath, src_list))
        windst = util.to_winpath(dst)
        # if all of elements are not None, windows binary mode
        if all(winsrc_list):
            log.info("Windows SRC detected")
            log.info("Windows binary mode")
            exe_from_wsl = True
            # iter<PureWindowsPath> to list[str]
            winsrc_list = list(map(str, winsrc_list))

    if iswin:
        if args.exclude or args.exclude_from:
            raise RuntimeError("--exclude and --exclude-from are unavailable for Robocopy")
        sync_win_robocopy(src_list, dst, args.exclude_file, args.exclude_dir, args.dry_run, args.force)
    elif exe_from_wsl:
        if args.exclude or args.exclude_from:
            raise RuntimeError("--exclude and --exclude-from are unavailable for Robocopy")
        sync_win_robocopy(winsrc_list, windst, args.exclude_file, args.exclude_dir, args.dry_run, args.force)
    else:
        if args.exclude_file or args.exclude_dir:
            raise RuntimeError("--exclude-file and --exclude-dir are unavailable for rsync")
        sync_unix_rsync(src_list, dst, args.exclude, args.exclude_from, args.dry_run, args.force)

    log.info("OK")


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Make a copy of file tree (Linux: rsync, Windows: robocopy)",
        epilog="Make sure of what will happen because sync operation may destruct the dest dir.",
    )
    parser.add_argument("--src", "-s", nargs="+",
                        help="backup source dir"
                        " (rsync: dir/ means all entries in the dir will be copied. dir means dir directory will be copied)")
    parser.add_argument("--dst", "-d", required=True, help="backup destination dir")
    parser.add_argument("--exclude", nargs="*", default=[], help="exclude patterns (rsync)")
    parser.add_argument("--exclude-from", nargs="*", default=[], help="exclude list files (rsync)")
    parser.add_argument("--exclude-file", nargs="*", default=[], help="exclude files (Robocopy)")
    parser.add_argument("--exclude-dir", nargs="*", default=[], help="exclude dirs (Robocopy)")
    parser.add_argument("--dry-run", "-n", action="store_true", help="dry run")
    parser.add_argument("--force", "-f", action="store_true", help="run without confirmation")

    args = parser.parse_args(argv[1:])

    sync(args)
