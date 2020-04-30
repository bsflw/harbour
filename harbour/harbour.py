#!/usr/bin/python3
import os
import shutil
import subprocess
import platform
import sys
import time
from typing import List, Optional

from gnupg2 import get_gnupg2_binary, try_verify_with_gpg2
from gnupgMock import gen_sign_status_messages, gen_verify_status_messages
from keybase import operations
from keybase.utils import get_fingerprint_from_id, get_keybase_binary
from result import VerifyResult

KEYBASE_BIN = get_keybase_binary()
GPG_BIN = get_gnupg2_binary()

if os.getenv("HARBOUR_USE_GNUPG2"):
    USE_GNUPG2 = True
else:
    USE_GNUPG2 = False


class VerifyResult(object):
    output: str
    returncode: int


def handle_error(error_output: str, returncode: int) -> Optional[str]:
    if "signature made by unknown entity" in error_output:
        return (
            "Keybase was unable to verify the signature: the public key is unknown.\n"
            + "To verify with your GnuPG2 keychain, set HARBOUR_USE_GNUPG2 in your shell."
        )
    else:
        return error_output


def verify(args: List[str]) -> None:
    """Use Keybase to verify a given commit and commit signature.

    If the environment variable HARBOUR_USE_GNUPG2 is set then, if Keybase fails
    to validate the key, GnuPG2 will be invoked to try to verify them.

    Arguments:
        args {List[str]} -- the arguments provided by Git when executing
    """

    input_file = sys.argv[-2]
    message = sys.stdin.read()
    # message = "".join([x.replace('\r\n', '\n') for x in sys.stdin.readlines()])

    keybase_process = subprocess.Popen(
        operations.verify(KEYBASE_BIN, input_file),
        # ["C:\\Users\\phild\\AppData\\Local\\Keybase\\keybase.EXE", "pgp", "verify", "--detached", input_file, "--infile", fp.name],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

    # On Linux, all output goes to stderr no matter what. But on Windows it
    # works correctly.
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        _, out = keybase_process.communicate(input=message)
    elif platform.system() == 'Windows':
        out, err = keybase_process.communicate(input=message)
    else:
        out, err = keybase_process.communicate(input=message)

    if "Signature verified." not in out:
        if USE_GNUPG2:
            result = try_verify_with_gpg2(GPG_BIN, input_file, message)

            print(result.output, file=sys.stderr)
            sys.exit(result.return_code)

        else:
            if err:
                err_msg = handle_error(
                    error_output=err, returncode=keybase_process.returncode
                )
            else:
                err_msg = handle_error(
                    error_output=out, returncode=keybase_process.returncode
                )
            print(err_msg, file=sys.stderr, flush=True)
            exit(keybase_process.returncode)

    # remove last newline
    out = "Keybase: " + out.replace(" (", "\n(").replace("\n\r", "n")[:-1]


    print(gen_verify_status_messages(), file=sys.stdout, flush=True)
    print(out, file=sys.stderr, flush=True)


def sign(args: List[str]) -> None:
    """Sign a given commit message with a specific provided key using Keybase.

    Arguments:
        args {List[str]} -- the arguments provided by Git
    """
    key = args[args.index("-bsau") + 1]

    message = "".join(sys.stdin.readlines())
    keybase_process = subprocess.Popen(
        operations.sign(KEYBASE_BIN, key),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )
    outs, errs = keybase_process.communicate(input=message)
    # remove last newline
    outs = outs.replace("\n\r", "n")[:-1]

    print(gen_sign_status_messages(), file=sys.stderr, flush=True)
    print(outs, flush=True)


def invalid_command(*args, **kwargs) -> None:
    print("Not a valid command", file=sys.stderr)
    sys.exit(1)


def main():
    """Detects if Keybase should sign or verify and runs those procedures.
    """

    func: callable = invalid_command

    # TODO: argparse instead
    # TODO: Add -h & --help
    for arg in sys.argv:
        # Why can't Git use full command argument names? What a mess.
        if arg == "-bsau":
            func = sign
        elif arg == "--verify":
            func = verify
        else:
            continue

    func(sys.argv)
    exit(0)


if __name__ == "__main__":
    main()
