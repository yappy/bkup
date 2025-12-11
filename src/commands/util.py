import os
import pathlib
import platform
import subprocess


_is_wsl: bool = None


def format_cmd(cmd: list[str]) -> str:
    return " ".join(map(lambda t: f'"{t}"', list))


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
