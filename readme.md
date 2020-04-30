# harbour

Use Keybase to sign and verify your Git commits. Currently, harbour has only
been tested on Linux but Windows and macOS support are coming soon.

## Getting started

Set the following in your `$HOME/.gitconfig`:

```git
[gpg]
    program = /home/$YOUR-NAME/.local/bin/harbour
[commit]
    gpgsign = true
[user]
    signingkey = <YOUR KEY FROM KEYBASE>
```

Coming soon; for now you'll have to put that big brain of yours to work.

## What? Why?

Well, there are lots of people online who show how you can export your PGP keys
from Keybase and import them into gnupg2, but that seems like it defeats the
point of using Keybase to begin with.

Harbour sits in-between Git and Keybase (without ever looking at your private
keys) and has can still verify signatures from your existing GnuPG2 keychain.

## How do I keep using my GnuPG2 keys to verify signatures?

Set HARBOUR_USE_GNUPG2 as an environment variable in your shell where you use
`git`. Then, whenever Git wants to verify a signature, Harbour will first try
to verify with Keybase and, if a signature can't be verified, will try again
with GnuPG2 

### One-time

```sh
HARBOUR_USE_GNUPG2=True git log --show-signature
```

### In your RC files

```bashrc
# $HOME/.bashrc
# or $HOME/.zshrc
# ... or anywhere else :)
set HARBOUR_USE_GNUPG2=True
```
