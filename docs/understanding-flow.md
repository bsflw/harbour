# Understanding the data flow

Gee these details took me way too long to figure out. Hopefully, if you redo what I did, you can use this as a starting place.

## Signing a commit

When you ask Git to sign a commit for you, a few things happen:

- Git invokes `gpg.program` (defined in your `$HOME/.gitconfig`) like so, in your current working directory. Below is an explanation of the command, including GnuPG2's full names for the flags.
    ```sh
    $GPG_PROGRAM --status-fd 2 -bsau $key
    ```
    - `--status-fd 2` means GnuPG should write it's status to "file descriptor 2", which is `stderr`. Git reads some of these messages later to determine what GPG did. These status messages are **required**.
    - `-b, --deatch-sign`: make a detached signature
    - `-s, --sign`: sign a message
    - `-a, --armor`: create ASCII armored output
    - `-u, --local-user USER-ID`: use `USER-ID` as the key to sign or decrypt with
    - `$key`: the user ID we sign with (see `-u`)
    
- GnuPG runs, and begins emitting messages to `stderr` like this:

    - ```
        [GNUPG:] KEY_CONSIDERED EEF512182D07605D6421EF14C7EDC89806F63BF3 2
        [GNUPG:] BEGIN_SIGNING H10
        [GNUPG:] SIG_CREATED D 1 10 00 1588223631 EEF512182D07605D6421EF14C7EDC89806F63BF3
        ```

- When it's made the signature it's happy with, GnuPG emits your signature on `stdout`, which is where Git picks it up.

    - ```PGP
        -----BEGIN PGP SIGNATURE-----
        
        iQIzBAABCgAdFiEE7vUSGC0HYF1kIe8Ux+3ImAb2O/MFAl6qXskACgkQx+3ImAb2
        O/PufA//QRXLUK9v4LzL3GSw1gzdjLoWWfDTnCC4GhR7IwU+MVui+v2gDliNg1IV
        0SqifZ45p7L1qYrO2Cq2HXj0p7w3PcNFA9a7iSR93cX7w+RXWW05pcPoCV9lxiYk
        iOTuIM6W1aSeCugiJ/v7iexd0UDNX+KYELy6yGTCsX/KaBtENx60suMeL59JdKgg
        UcGgCgj9uJHDRsqx6VH5nMGOxWGvbtG2TzhUvj2SWJrRuRlp3ZZhDJP02HOd6MAg
        PqzJyTeqrJq+gpL+Yr4D16fF87tPIPEUE6DRP6PhQ59PPfl3PbzpnsrgDPgtgQwn
        GBk8N/EFn4IFPph7jrI5WJWw6W3pWZ2u4ydlFjMPOaXMQg5Lvn927Iy65hXGwMD2
        zA4NvbBFo/2NsrjQ8gVk9zHem6aP4vb3neFljl0/wHT3Qz/tKka73bKoF26IypoM
        UKWJ5alr0LsnDS1oQh5PWZYuFQL8SBgTk5VUn7aOCnjGZcj5p+WSDQB55Mb8DW+R
        O/zX9iNaroXnvrcP+5JeZhiUghEqTJq9kpNwMYZU8n+NG/mApPnBa4SoAQ/bfCbU
        Bpf9m9WW1fShWjGNA8zdCTu5Sb6x9gBi9LPVhCAQ37ZqHcCw38LEvmEfJrOUYpRG
        aV2k8arjIwaBcmie4vmk7LDYlTVgD0hS3+bfg4hCo5Qaa/RGoi0=
        =UpPO
        -----END PGP SIGNATURE-----
        ```
    
- Git reads `stderr` and checks that it contains `"\n[GNUPG:] SIG_CREATED "` [^sig-created-git] . If not, Git will error and state that "gpg failed to signed the data". If is satisfied that GPG succeeded, Git reads the PGP signature to verify it's not garbage and tucks it away for later.

    [^sig-created-git]: hgit/gpg-interface.c line 454 commit d61d20c https://github.com/git/git/blob/d61d20c9b413225793f8a0b491bbbec61c184e26/gpg-interface.c

    

## Verifying commits



## GnuPG status header details

Not needed for Harbour, but damn it I spent time researching this stuff; I'm going to write it down!

- `KEY_CONSIDERED <ke_fingerprint>` is a key that's trying to be used for signing

- `BEGIN_SIGNING` (obvious)

- `SIG_CREATED <type> <pk_algo> <hash_algo> <class> <timestamp> <key_fingerprint>`
	- `type` is D for "detached"
	- `pk_algo` is "1" for RSA+RSA (see "Algorithm names for the "keygen.algo" prompt" in gnupg2/doc/DETAILS)
	- `hash_algo` and `class`: no idea
	- `key_fingerprint` is the fingerprint of the signing key under consideration

### More details

Check out [gnupg2's doc/DETAILS file](https://git.gnupg.org/cgi-bin/gitweb.cgi?p=gnupg.git;a=tree;f=doc;h=141111413578a55231976f11aed4639ad6879679;hb=refs/heads/master) and [git's source code](https://github.com/git/git/blob/d61d20c9b413225793f8a0b491bbbec61c184e26/gpg-interface.c).