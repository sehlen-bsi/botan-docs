
def check_keys(artefact: str, keys: list[str], expected_keys: list[str]):
    unexpected_keys = [k for k in keys if k not in expected_keys]
    if unexpected_keys:
        raise RuntimeError("Unexpected key(s) '%s' in %s" % (','.join(unexpected_keys), artefact))
