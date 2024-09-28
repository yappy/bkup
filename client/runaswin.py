#!/usr/bin/env python3

import sys
import platform
import pathlib
import subprocess


# Convert WSL (Linux) path to Windows path
# Example:
#   /mnt/c/Windows => C:\Windows
#   /etc => \\wsl.localhost\Debian\etc
def wslpath_to_win(wslpath):
    proc = subprocess.run(
        ["wslpath", "-w", str(wslpath)],
        check=True, text=True, stdout=subprocess.PIPE, stderr=None)
    return pathlib.PureWindowsPath(proc.stdout.strip())


def usage(argv0: str):
    print(f"""
{argv0}: Execute python script on Windows
    Usage: {argv0} PYFILE [ARGS...]")

PYFILE and current directory will be automatically translated to Windows path.
ARGS will be passed to the program as is.
"""[1:-1])


def main(argv: list[str]):
    if platform.system() != "Linux":
        print("This is WSL only")
        sys.exit(1)

    if len(argv) < 2:
        usage(argv[0])
        sys.exit(1)

    # convert path if the first argument is not -flags
    if argv[1].startswith("-"):
        argv1 = argv[1]
    else:
        argv1 = str(wslpath_to_win(argv[1]))
    # "*.exe" in WSL makes Windows program run
    cmd = ["py.exe", "-3", argv1] + argv[2:]

    print("Execute Windows python...")
    print(f"Run: {' '.join(cmd)}")
    print("-" * 80)
    try:
        subprocess.run(cmd, check=True)
        print("-" * 80)
        print("Windows python exited successfully")
    except subprocess.CalledProcessError as e:
        print("-" * 80)
        print(f"Error: Windows python exited with exitcode={e.returncode}")
        sys.exit(e.returncode)
    except BaseException:
        print("-" * 80)
        print("""
Exec py.exe error:
Please confirm that Windows python (NOT a MS store version) is available.
Then it is needed to restart WSL.
> winget.exe search python.python
> winget.exe install Python.Python.3.x
> wsl.exe --shutdown
"""[1:])
        raise


if __name__ == '__main__':
    main(sys.argv)
