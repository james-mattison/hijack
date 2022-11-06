#!/usr/bin/env python3
import fcntl
import getpass
import os
import termios
import time
import sys
import argparse
import subprocess

USAGE = """
hj <TTY> <COMMAND> [-s/--strip]
hj list

-s/--strip: remove the carriage return from <COMMAND>

<COMMAND> may contain shortcuts:
  :br -> send break
  :cr -> send \n
  :d -> send EOT, closing the TERM session
  :logout -> force log the user out
  :cr -> hit return
"""
parser = argparse.ArgumentParser(usage=USAGE, description=argparse.SUPPRESS)
parser.add_argument("tty", action="store")
parser.add_argument("command_chunks", nargs="*")
parser.add_argument("-s", "--strip", action = "store_true", default = False, help = "Strip newline from the command?")


class HijackException(Exception):

    def __init__(self, message: str):
        self._message = message

    def __str__(self):
        return self._message


class TTYPipe:
    """
    Methods for command injection into teletype terminals.
    """

    def __init__(self, tty_name: str):
        self.pipe = self._validate_pipe(tty_name)

    @staticmethod
    def _validate_pipe(dev_tty: str):
        """

        """
        if not os.path.exists(dev_tty):
            if not os.path.exists(os.path.join("/dev", dev_tty)):
                raise HijackException(f"Invalid pipe - no such file {dev_tty}")
            else:
                dev_tty = os.path.join("/dev", dev_tty)

        _pipe = os.open(dev_tty, os.O_RDWR)

        if not _pipe:
            raise HijackException(f"Unable to open valid pipe to {dev_tty}.")

        return _pipe

    def inject(self, command_blob: str, *, strip: bool = False, interval: float = 0.0, silent: bool = True) -> str:
        """
        Inject `command_blob`, character by character, into another tty.
        If `strip`, then does not hit enter after (ie, types but does not execute).
        If `interval`, then wait `interval` seconds between each injected character.
        Returns the entire command injected into the TTY.
        """
        injected = []

        assert isinstance(command_blob, str)
        # Assume we want to execute a command, rather than just type something.
        if not command_blob.endswith("\n") and not strip:
            command_blob += "\n"

        # Insert, character-by-character, the command blob. If an interval has been specified, wait that long between
        # characters:
        for i in range(len(command_blob)):
            if interval:
                time.sleep(interval)
            fcntl.ioctl(self.pipe, termios.TIOCSTI, command_blob[i])
            injected.append(command_blob[i])
            if not silent:
                print(command_blob[i], end="", flush=True)
        return "".join(injected)

    def send_eot(self):
        """Send the end-of-transmission character (ctrl + D)"""
        self.inject(str(u"\u0004"))

    def send_break(self):
        self.inject(str(u"\u0003"))

    def terminate_session(self):
        """Terminate the selected TTY session by sending BREAK followed by EOT"""
        self.send_break()
        self.send_eot()

    def send_return(self):
        """Send a carriage return"""
        self.inject("\n")

    def cr(self):
        """Same as send_return"""
        self.send_return()

    def logout_session(self):
        """ Log the user out of his current session"""
        self.send_break()
        self.send_eot()
        self.inject("kill $$")

    @staticmethod
    def list_ttys():
        """
        List active TTYs and their users.
        """
        users = []
        w = subprocess.getoutput("PROCPS_USERLEN=20 w -h")
        lines = w.split("\n")

        for line in lines:
            chunks = line.split()
            data = {"user": chunks[0],
                    "tty": f"/dev/{chunks[1]}"
                    }
            users.append(data)
            print(f"User: {data['user']} / TTY: {data['tty']}")


if __name__ == '__main__':
    if getpass.getuser() != "root":
        raise HijackException(f"You must be root to use {sys.argv[0]}")

    args = parser.parse_args()
    if args.tty == "list":
        TTYPipe.list_ttys()
        quit(0)
    pipe = TTYPipe(args.tty)


    def parse_shortcut(shortcut: str):
        """
        Determine if we got any shortcuts as the first word in the command string
        """
        shortcuts = {
            pipe.send_break: {
                "help": "Send SIGINT into the target TTY",
                "verbs": [":br", ":br:", ":b:", ":break", ":break:"]
            },
            pipe.send_eot: {
                "help": "Send SIGEND (Ctrl + D) to the target TTY",
                "verbs": [":d", ":d:", ":eof:", ":eot", ":eot:"]
            },
            pipe.terminate_session: {
                "help": "Forcibly terminate that user's session (for logout)",
                "verbs": [":lo", ":lo:", ":logout", ":logout:"]
            },
            pipe.send_return: {
                "help": "Hit the enter key (\\n)",
                "verbs": [":\\n:", ":\\n"]
            }
        }

        for _cb, val in shortcuts.items():
            if shortcut in val["verbs"]:
                return _cb

        return ""


    cmd = ""

    for arg in args.command_chunks:
        cb = parse_shortcut(arg)
        if cb:
            cb()
        else:
            cmd += " " + str(arg)

        if cmd.strip():
            pipe.inject(cmd, strip = args.strip)
