import logging
import argparse
import pathlib
import subprocess

log = logging.getLogger(__name__)


def upload(args: argparse.Namespace):
    src = pathlib.Path(args.src)
    latest = src / "latest.txt"

    log.info(f"Read the latest archive: {str(latest)}")
    with latest.open() as fin:
        latest_file = src / fin.readline().strip()
    log.info(f"The latest archive: {str(latest_file)}")
    if not latest_file.is_file():
        raise RuntimeError(f"{str(latest_file)} is not a valid file")

    cmd = [
        "rsync",
        # archive mode (=-rlptgoD), compress, skip if dst is newer
        "-azu",
    ]
    if args.ssh:
        cmd += [
            "-e",
            args.ssh,
        ]
    cmd += [
        # SRC
        str(latest_file),
        # DST
        args.dst,
    ]

    log.info(" ".join(cmd))
    subprocess.run(cmd, check=True)

    log.info("OK")


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Archive and compress a directory (Linux: tar.bz2, Windows: 7z)",
    )
    parser.add_argument("--src", "-s", required=True, help="archive dir")
    parser.add_argument("--dst", "-d", required=True, help="rsync destination (user@host:dir)")
    parser.add_argument("--ssh", help='ssh command line (e.g. --ssh "ssh -p 12345")')
    parser.add_argument("--dry-run", "-n", action="store_true", help="dry run")

    args = parser.parse_args(argv[1:])

    upload(args)
