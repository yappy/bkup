import logging
import argparse
import pathlib
import subprocess

log: logging.Logger = logging.getLogger(__name__)


def upload(args: argparse.Namespace):
    src = pathlib.Path(args.src)
    latest = src / "latest.txt"

    log.info(f"Read the latest archive: {str(latest)}")
    with latest.open() as fin:
        latest_file = src / fin.readline().strip()
    log.info(f"The latest archive: {str(latest_file)}")
    if not latest_file.is_file():
        raise RuntimeError(f"{str(latest_file)} is not a valid file")

    dst: str = args.dst
    if not dst.endswith("/"):
        dst += "/"

    cmd = [
        "rsync",
        # archive mode (=-rlptgoD), use checksum to check if the file is changed
        "-acv",
        # backup data may contain sensitive data
        # set permission dir=700, file=600 (owner only)
        "--chmod=D700,F600"
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
        dst,
    ]

    log.info(" ".join(cmd))
    subprocess.run(cmd, check=True)

    log.info("OK")


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Copy the latest archive file to a remote host by rsync",
    )
    parser.add_argument("--src", "-s", required=True, help="archive dir")
    parser.add_argument("--dst", "-d", required=True, help="rsync destination (user@host:dir)")
    parser.add_argument("--ssh", help='ssh command line (e.g. --ssh "ssh -p 12345")')
    parser.add_argument("--dry-run", "-n", action="store_true", help="dry run")

    args = parser.parse_args(argv[1:])

    upload(args)
