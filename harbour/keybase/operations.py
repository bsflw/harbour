from typing import List


def list(keybase_binary: str) -> List[str]:
    return [keybase_binary, "pgp", "list"]


def verify(keybase_binary: str, input_file: str) -> List[str]:
    return [keybase_binary, "pgp", "verify", "--detached", input_file, "--infile", "-"]


def sign(keybase_binary: str, key: str) -> List[str]:
    return [keybase_binary, "pgp", "sign", "--detached", "-k", key]
