import sys
from shutil import which
from subprocess import PIPE, Popen
from typing import Optional

from result import VerifyResult


def get_gnupg2_binary() -> Optional[str]:
    possible_names = ["gpg2", "gpg"]

    for name in possible_names:
        path = which(name)
        if path:
            proc = Popen([path, "--version",], stdout=PIPE, encoding="utf-8",)
            raw_text = "".join(proc.stdout.readlines())
            version_number = raw_text.split(" ")[2]
            if float(version_number[:3]) > 2.0:
                return path

    return None


def try_verify_with_gpg2(
    gpg2_binary, signature_file: str, message_contents: str
) -> VerifyResult:
    proc = Popen(
        [
            gpg2_binary,
            "--status-fd",
            "1",
            "--keyid-format",
            "long",
            "--verify",
            signature_file,
            "-",
        ],
        stdin=PIPE,
        stderr=PIPE,
        encoding="utf-8",
    )

    # All output goes to stderr no matter what
    _, out = proc.communicate(input=message_contents)
    return VerifyResult(output=out[:-1], return_code=proc.returncode)
