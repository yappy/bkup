#!/usr/bin/env python3

import sys
import commands
import logging

def log_init():
    logging.basicConfig(
        format='%(asctime)s %(levelname)8s:%(name)16s: %(message)s',
        #format='%(asctime)s %(levelname)8s:%(name)16s:%(lineno)4s: %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

def usage(argv0: str):
    print(f"{argv0} SUBCMD [args...]")
    print("Subcommands")
    for _func, name, desc in commands.command_table:
        print(f"* {name}")
        print(f"    {desc}")

def main(argv: list[str]):
    log_init()

    if len(argv) < 2 or argv[1] == "--help" or argv[1] == "-h":
        usage(argv[0])
        sys.exit(0)

    subcmd = argv[1]
    args = argv[2:]
    found = False
    for func, name, _desc in commands.command_table:
        if name == subcmd:
            func([subcmd] + args)
            found = True
            break
    if not found:
        print(f"Subcommand not found: {subcmd}")
        print()
        usage(argv[0])
        sys.exit(1)

if __name__ == '__main__':
    main(sys.argv)
