import logging
import os
import pathlib
import platform
import subprocess

log: logging.Logger = logging.getLogger(__name__)

_is_wsl: bool = None


# Print command and run
def exec(cmd: list[str], *, dry_run: bool = False, cwd: str | None = None, check: bool = True):
    log.info(f"EXEC: {' '.join(cmd)}")
    if not dry_run:
        return subprocess.run(cmd, check=check, cwd=cwd).returncode
    else:
        log.info("dry_run")
        return 0


# Print command, run, and capture stdout (stderr will be as is)
def exec_out(cmd: list[str], *, dry_run: bool = False) -> str:
    log.info(f"EXEC: {' '.join(cmd)}")
    if not dry_run:
        proc = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=None)
        return proc.stdout
    else:
        log.info("dry_run")
        return ""


def is_wsl() -> bool:
    global _is_wsl
    if _is_wsl is not None:
        return _is_wsl

    try:
        # ignore exit code and output
        subprocess.run(
            ["wslpath"], check=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        _is_wsl = False
        return _is_wsl

    _is_wsl = True
    return _is_wsl


def is_win() -> bool:
    return platform.system() == "Windows"


def to_winpath(wslpath: os.PathLike) -> pathlib.PureWindowsPath | None:
    assert is_wsl()

    proc = subprocess.run(
        ["wslpath", "-wa", str(wslpath)],
        check=True, text=True, stdout=subprocess.PIPE, stderr=None)
    result = proc.stdout.strip()

    if result.startswith("\\\\wsl"):
        return None
    else:
        return pathlib.PureWindowsPath(result)


def to_wslpath(winpath: os.PathLike) -> pathlib.Path:
    assert is_wsl()

    proc = subprocess.run(
        ["wslpath", "-ua", str(winpath)],
        check=True, text=True, stdout=subprocess.PIPE, stderr=None)

    return proc.stdout.strip()


# Win/WSL only
def get_winenv(name: str) -> str:
    if is_win():
        return os.getenv(name, "")
    else:
        assert is_wsl()
        proc = subprocess.run(
            ["powershell.exe", f"$env:{name}"],
            check=True, text=True, stdout=subprocess.PIPE, stderr=None)

        return proc.stdout.strip()


# Win/WSL only
def get_winuser() -> str:
    return get_winenv("UserName")
