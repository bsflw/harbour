package main

import (
	"bytes"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"strings"
)

// VerifyResult does the thing
type VerifyResult struct {
	returnCode int
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

// Contains returns true if a contains x.
func contains(a []string, x string) bool {
	for _, n := range a {
		if x == n {
			return true
		}
	}
	return false
}

// Returns the index of string x in a, if it exists, and -1 if not.
func indexOf(a []string, x string) int {
	for i, n := range a {
		if x == n {
			return i
		}
	}
	return -1
}

func getGnupg2Binary() string {
	path, err := exec.LookPath("gpg2")
	if err != nil {
		log.Fatal("GnuPG2 is not installed (or gpg2 isn't in your $PATH)")
	}
	return path
}

func tryVerifyWithGpg2(
	signatureFile string,
	messageContents string) VerifyResult {

	cmd := exec.Command(
		getGnupg2Binary(),
		"--status-fd",
		"1",
		"--keyid-format",
		"long",
		"--verify",
		signatureFile,
		"-")

	// Use a stdin pipe for writing the message contents into
	stdin, err := cmd.StdinPipe()
	check(err)

	// Send GPG2 the message
	go func() {
		defer stdin.Close()
		io.WriteString(stdin, messageContents)
	}()

	// Git expects both stderr and stdout, so we may as well
	// re-use the pipes Harbour uses
	cmd.Stderr = os.Stderr
	cmd.Stdout = os.Stdout

	// Execute gpg2
	gpgErr := cmd.Run()
	if gpgErr != nil {
		// If there was an error, we report it to the higher ups
		return VerifyResult{-1}
	}
	// Otherwise return like all is well.
	return VerifyResult{0}
}

func keybaseCliList() []string {
	return []string{"pgp", "list"}
}

func keybaseCliVerify(inputFile string) []string {
	return []string{"pgp", "verify", "--detached", inputFile, "--infile", "-"}
}

func keybaseCliSign(key string) []string {
	return []string{"pgp", "sign", "--detached", "-k", key}
}

func getKeybaseBinary() (string, error) {
	var possibleNames = []string{"keybase", "keybase.exe"}

	for _, name := range possibleNames {
		path, err := exec.LookPath(name)
		if err == nil {
			return path, nil
		}
	}

	return "", errors.New("Couldn't find Keybase on your $PATH")
}

func getFingerprintFromID(keyID string) string {
	fingerprint := ""
	keybaseBin, err := getKeybaseBinary()
	if err != nil {
		return ""
	}

	out, err := exec.Command(keybaseBin, keybaseCliList()...).Output()
	if err != nil {
		log.Fatal(err)
	}

	outString := string(out)
	matchString := "PGP Fingerprint: "

	for _, line := range strings.Split(strings.TrimSuffix(outString, "\n"), "\n") {
		if strings.HasPrefix(line, matchString) && strings.HasSuffix(line, keyID) {
			fingerprint = strings.Split(line, matchString)[1]
			break
		}
	}

	return fingerprint
}

func verify(args []string) VerifyResult {
	// Use Keybase to verify a given commit and commit signature.
	//
	// If the environment variable HARBOUR_USE_GNUPG2 is set, then we use
	// GnuPG2 if Keybase cannot validate the key.

	inputFile := args[len(args)-2]
	messageBytes, err := ioutil.ReadAll(os.Stdin)
	check(err) // fail if we can't read stdin from git
	message := string(messageBytes)

	keybaseBin, err := getKeybaseBinary()
	check(err) // fail if there's no Keybase binary

	// Run the verify command in Keybase and capture standard out
	procVerify := exec.Command(keybaseBin, keybaseCliVerify(inputFile)...)
	stdin, err := procVerify.StdinPipe()
	check(err) // fail if we can't open a pipe to Keybase

	// Write the commit message to stdin to be verified by Keybase
	go func() {
		defer stdin.Close()
		io.WriteString(stdin, message)
	}()

	// We'll need to parse the output before sending it to Git to make sure
	// Keybase verified the signature; if not, we may want to try GnuPG2
	var stderr bytes.Buffer
	procVerify.Stderr = &stderr
	err = procVerify.Run()

	errString := string(stderr.Bytes())

	// Note that on Linux keybase prints signature verification to stderr.
	// No idea why.
	if err != nil || !strings.Contains(errString, "Signature verified.") {
		// Keybase couldn't verify the commit
		_, useGnupg2 := os.LookupEnv("HARBOUR_USE_GNUPG2")
		if useGnupg2 {
			fmt.Println("Trying GnuPG2")
			return tryVerifyWithGpg2(inputFile, message)
		}

		fmt.Println("Keybase was unable to verify the signature: the public key is unknown.\n" + "To verify with your GnuPG2 keychain, set HARBOUR_USE_GNUPG2 in your shell.")
	} else {
		// Keybase verified the commit
		// git expects this string to show up in stderr; that's how it verifies the
		// signature was generated.
		io.WriteString(os.Stdout, "\n[GNUPG:] GOODSIG \n")
		// Prepend Keybase's messsage with a label
		io.WriteString(os.Stderr, "Keybase: ")

		// Make the output prettier by adding a newline after
		// "Signature verified."
		output := strings.Split(errString, "Signature verified. ")[1]

		// Ouput the verification message to git
		io.WriteString(os.Stderr, "Signature verified.\n")
		io.WriteString(os.Stderr, output)
	}

	return VerifyResult{returnCode: procVerify.ProcessState.ExitCode()}
}

func sign(args []string) {
	// Sign a given commit message with a specific key using Keybase.

	// The key ID follows the -u flag
	key := args[indexOf(args, "-bsau")+1]
	messageBytes, err := ioutil.ReadAll(os.Stdin)
	check(err) // fail if we can't read stdin from git; this is what we sign
	message := string(messageBytes)

	keybaseBin, err := getKeybaseBinary()
	check(err) // fail if there's no Keybase binary

	// Run the sign command in Keybase and capture standard out
	procSign := exec.Command(keybaseBin, keybaseCliSign(key)...)

	stdin, err := procSign.StdinPipe()
	check(err) // fail if we can't open a pipe to Keybase

	// Write the commit message to stdin to be verified by Keybase
	go func() {
		defer stdin.Close()
		io.WriteString(stdin, message)
	}()

	// We don't need to process the output, so we'll share our stdout/stderr
	// pipes with Keybase
	procSign.Stdout = os.Stdout
	procSign.Stderr = os.Stderr
	err = procSign.Run()
	check(err)
	io.WriteString(os.Stderr, "\n[GNUPG:] SIG_CREATED \n")
}

func main() {
	if contains(os.Args, "--verify") {
		result := verify(os.Args)
		os.Exit(result.returnCode)
	} else if contains(os.Args, "-bsau") {
		sign(os.Args)
	} else {
		fmt.Println("That's not a valid command. Use Harbour by setting your gpg program to it in your .gitconfig.")
		os.Exit(1)
	}
}
