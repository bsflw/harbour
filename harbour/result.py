class VerifyResult(object):
    output: str
    return_code: int

    def __init__(self, output: str, return_code: str):
        """The result of trying to verify a signature.

        Arguments:
            output {str} -- The text to send to Git
            return_code {str} -- The verifying processes code when it exited.
        """
        self.output = output
        self.return_code = return_code
