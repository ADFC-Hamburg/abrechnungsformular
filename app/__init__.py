def _fetch_version(path:str) -> str:
    with open(path) as f:
        version = f.readline()
    return version

#: Die Versionsnummer dieser App.
VERSION = _fetch_version('VERSION')
