import yaml

from auditinfo.botan import auditors_file_path

class Auditor:
    def __init__(self, name: str, github_handle: str):
        self.name = name
        self.github_handle = github_handle[1:] if github_handle.startswith('@') else github_handle

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.github_handle == other.github_handle

    def __hash__(self):
        return self.github_handle.__hash__()

def authorative_auditors() -> list[Auditor]:
    auditors_file = auditors_file_path()
    strm = open(auditors_file, 'r')
    cfg = yaml.load(strm, Loader=yaml.FullLoader)
    if not cfg:
        raise RuntimeError("Failed to load auditor configuation: %s" % auditors_file)
    return [Auditor(auditor['name'], auditor['github']) for auditor in cfg['auditors']]


