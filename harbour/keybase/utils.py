import enum
from shutil import which
from subprocess import PIPE, Popen
from typing import List, Optional


def get_keybase_binary() -> Optional[str]:
    possible_names = ["keybase", "keybase.exe"]

    for name in possible_names:
        path = which(name)
        if path:
            return path

    return None


def get_fingerprint_from_id(key_id: str) -> Optional[str]:
    """Returns the first fingerprint of a PGP key that matches ``key_id``

    Arguments:
        key_id {str} -- The short ID of teh PGP key you want a fingerprint of.

    Returns:
        Optional[str] -- The matching fingerprint, if one was found. None otherwise.
    """

    fingerprint: str = None
    proc = Popen(LIST(), stdout=PIPE, encoding="utf-8")

    # We're trying to find match_str in any of the outut lines of proc first,
    # then we look for key_id
    match_str = "PGP Fingerprint: "
    for line in proc.stdout:
        line_santised = line.strip()

        if line_santised.startswith(match_str):
            if line_santised.lower().endswith(key_id.lower()):
                # Take only what's after match_str and make it uppercase to
                # match what GnuPG 2 does.
                fingerprint = line_santised.split(match_str)[1].upper()
                break

    return fingerprint
