def gen_sign_status_messages() -> str:
    """Returns GnuPG2-like status messages that Git requires to accept
    PGP signatures.

    Returns:
        Optional[str] -- Status messages for sending to Git
    """
    return "\n[GNUPG:] SIG_CREATED \n"


def gen_verify_status_messages() -> str:
    """Returns a GnuPG2-like status that Git interprets as a "good signature"

    Returns:
        str -- Status messages for sending to Git
    """
    return "\n[GNUPG:] GOODSIG \n"
