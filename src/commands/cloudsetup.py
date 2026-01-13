import logging
import argparse
import subprocess
import platform
import tempfile
from . import util

log: logging.Logger = logging.getLogger(__name__)


def get_current_version() -> str | None:
    try:
        tokens = util.exec_out(["rclone", "version"]).split()
        assert len(tokens) >= 2
        assert tokens[0] == "rclone"
        assert tokens[1].startswith("v")
        return tokens[1]
    except subprocess.CalledProcessError as e:
        log.warning("rclone version failed")
        log.warning(e)
        return None


def get_latest_version() -> str:
    URL = "https://downloads.rclone.org/version.txt"

    log.info(f"Download: {URL}")
    tokens = util.exec_out(["wget", "-q", "-O", "-", URL]).split()
    assert tokens[0] == "rclone"
    assert tokens[1].startswith("v")
    return tokens[1]


def compare_version(v1: str, v2: str) -> int:
    def parse(ver: str) -> tuple[int, int, int]:
        assert ver.startswith("v")
        nums = list(map(int, ver[1:].split(".")))
        assert len(nums) == 3
        return nums[0], nums[1], nums[2]

    v1 = parse(v1)
    v2 = parse(v2)
    if v1[0] != v2[0]:
        return v1[0] - v2[0]
    elif v1[1] != v2[1]:
        return v1[1] - v2[1]
    else:
        return v1[2] - v2[2]


def download_latest():
    if platform.system() != "Linux":
        return

    arch = ""
    match platform.machine():
        case "x86_64" | "AMD64":
            arch = "amd64"
        case "armv7l":
            arch = "arm-v7"
        case "aarch64":
            arch = "arm64"
        case _ as machine:
            raise RuntimeError(f"Unknown arch: {machine}")
    FILE = f"rclone-current-linux-{arch}.deb"
    URL = f"https://downloads.rclone.org/{FILE}"

    tmpd = tempfile.TemporaryDirectory(delete=False, ignore_cleanup_errors=True)
    try:
        log.info(f"Downloading {URL} into {tmpd.name}")
        util.exec(["wget", URL], cwd=tmpd.name)
        log.info("Download OK!")
        log.info(f"INSTALL CMD: dpkg -i {tmpd.name}/{FILE}")
    except BaseException:
        tmpd.cleanup()
        raise


def cloudsetup(args: argparse.Namespace):
    cur = get_current_version()
    if cur is not None:
        log.info(f"Current rclone: {cur}")
    else:
        log.info("rclone is not installed?")

    latest = get_latest_version()
    log.info(f"Latest rclone: {latest}")

    if cur is not None and compare_version(cur, latest) >= 0:
        return

    log.warning("Install the latest rclone!")
    log.warning("See: https://rclone.org/downloads/")
    download_latest()


def main(argv: list[str]):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description="Setup rclone tool",
        epilog="This is rclone wrapper",
    )

    args = parser.parse_args(argv[1:])

    cloudsetup(args)
