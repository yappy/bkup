import logging
import argparse
import pathlib
import subprocess
import datetime

log = logging.getLogger(__name__)

DOCKER_IMAGE = "busybox:latest"
DOCKER_MP_DEST = "/tmp/dest"
DOCKER_MP_VOLUME = "/tmp/vol"
EXT = "tar.bz2"


def exec(cmd: list[str], dry_run: bool):
    log.info(f"EXEC: {' '.join(cmd)}")
    if not dry_run:
        subprocess.run(cmd, check=True)
    else:
        log.info("dry_run")


def run_tar(project: str, volumes: list[str], ar_dst: pathlib.Path, dry_run: bool):
    vol_names = map(lambda v: f"{project}_{v}", volumes)
    ar_dst = ar_dst.absolute()
    ar_dir = ar_dst.parent
    ar_name = ar_dst.name
    try:
        cmd = ["docker", "run", "--rm"]
        # mount destination (bind)
        cmd += ["-v", f"{ar_dir}:{DOCKER_MP_DEST}"]
        # mount volumes
        for vol in vol_names:
            cmd += ["-v", f"{vol}:{DOCKER_MP_VOLUME}/{vol}"]
        # image
        cmd.append(DOCKER_IMAGE)
        # tar command in the container
        # a: auto detect compression by EXT
        # c: create
        # f: archive file name
        cmd += ["tar", "acf", f"{DOCKER_MP_DEST}/{ar_name}", "-C", f"{DOCKER_MP_VOLUME}", "."]
        exec(cmd, dry_run)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            # Warning (Non fatal error(s)).
            log.warning("tar exit with warning(s)")
        else:
            raise


def archive(args: argparse.Namespace):
    # mkdir DST
    dst = pathlib.Path(args.dst).expanduser().resolve()
    dst.mkdir(parents=True, exist_ok=True)
    if not dst.is_dir():
        raise RuntimeError("DST must be a directory")
    log.info(f"mkdir: {dst}")

    # datetime
    dt_now = datetime.datetime.now()
    dt_str = dt_now.strftime('%Y%m%d%H%M')

    ar_dst = dst / f"{args.project}_{dt_str}.{EXT}"
    log.info(f"DST: {ar_dst}")
    run_tar(args.project, args.volume, ar_dst, args.dry_run)

    # write ar_dst (not win_ar_dst) to latest.txt
    latest = dst / "latest.txt"
    log.info(f"Write the latest archive name: {str(latest)}")
    if not args.dry_run:
        with latest.open("w") as fout:
            print(ar_dst, file=fout)
    log.info(f"OK: {ar_dst}")


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Archive and compress a directory (Linux: tar.bz2, Windows: 7z)",
    )
    parser.add_argument("--project", "-p", required=True, help="Docker compose project name")
    parser.add_argument("--volume", "-v", action="append", required=True,
                        help="Docker volume name to back up (excluding project name) (multiple OK)")
    parser.add_argument("--dst", "-d", required=True, help="backup destination dir")
    parser.add_argument("--dry-run", "-n", action="store_true", help="dry run")

    args = parser.parse_args(argv[1:])

    archive(args)
