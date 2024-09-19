import tomllib

def _as_toml_value(v):
    vstr = ""
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

def as_toml(obj: dict):
    toml = ""
    for k, v in obj.items():
        vstr = _as_toml_value(v)
        toml += f'{k} = {vstr}\n'
    # parse test
    tomllib.loads(toml)

    return toml
