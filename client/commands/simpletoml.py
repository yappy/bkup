import tomllib
import sys
import argparse

def _as_toml_value(v) -> str:
    vstr = ""
    if v is None:
        raise ValueError("None is not allowed")
    if type(v) is str:
        esc = v.replace('"', '\\"').replace('\\', '\\\\')
        vstr = f'"{esc}"'
    elif type(v) is bool:
        vstr = str(v).lower()
    elif type(v) is list:
        if v:
            vstr += "[ "
            vstr += ", ".join(map(_as_toml_value, v))
            vstr += " ]"
        else:
            vstr += "[ ]"
    else:
        vstr = str(v)

    return vstr

def as_toml(obj: dict) -> str:
    """Convert given dict into TOML string.
    """
    toml = ""
    for k, v in obj.items():
        vstr = _as_toml_value(v)
        toml += f'{k} = {vstr}\n'
    # parse test
    tomllib.loads(toml)

    return toml

def as_toml_comment(s: str) -> str:
    toml = ""
    for line in s.splitlines():
        toml += f"# {line}\n"

    return toml

def parse_with_toml(parser: argparse.ArgumentParser, argv1: list[str]) -> argparse.Namespace:
    """Execute parse, then if --toml or --print-toml is specified,
    do appropriate things.

    parser must have "toml" and "print_toml" keys.
    """

    assert parser.get_default("toml") is not None
    assert parser.get_default("print_toml") is not None

    args = parser.parse_args(argv1)

    # if --toml, set it as defaults and parse again
    if args.toml:
        with open(args.toml, "rb") as f:
            data = tomllib.load(f)
            parser.set_defaults(**data)
            args = parser.parse_args(argv1)

    if args.print_toml:
        toml = as_toml_comment(parser.format_help())
        toml += "\n"
        defs = parser.parse_args([])
        toml += as_toml(vars(defs))
        print(toml, end="")
        sys.exit(0)

    return args
