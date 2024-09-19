#!/usr/bin/env python3

import sys
import commands

def usage(argv0: str):
	print(f"{argv0} SUBCMD [args...]")
	print("Sub Commands")
	for _func, name, desc in commands.command_table:
		print(f"* {name}")
		print(f"    {desc}")

def main(argv: list[str]):
	if len(argv) < 2 or argv[1] == "--help" or argv[1] == "-h":
		usage(argv[0])
		sys.exit(1)

	subcmd = argv[1]
	args = argv[2:]

if __name__ == '__main__':
	main(sys.argv)
