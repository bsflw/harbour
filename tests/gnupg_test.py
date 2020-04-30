import unittest

from harbour import gnupg2


class TestGnupg2Compat(unittest.TestCase):
    def test_gpg2_verify(self):
        """Check that when GPG2 verifies a commit for a key it doesn't know, it
        rejects the signature.
        """
        with open("tests/data/unknown/msg") as msg_file:
            contents = "".join(msg_file.readlines())
        signature_file = "tests/data/unknown/sig"
        result: Result.VerifyResult = Gnupg2.try_verify_with_gpg2(
            signature_file, contents
        )

        self.assertEqual(result.return_code, 2)
        self.assertIn("Can't check signature: No public key", result.output)


if __name__ == "__main__":
    unittest.main()
