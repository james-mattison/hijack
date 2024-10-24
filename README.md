## hijack

---

This tool allows injection of commands into another user's tty.



Also allows injection into another user's SSH session. You can inject literal BASH commands into the other user's TTY _as that user_.

The other user sees the commad that is entered into their terminal, and also gets all the output from the command (but you can certainly pipe the output to a place where you can also read it.)

#### **Example:**

You can run the command 

```bash
hj tty002 echo hello` 
```

... to run the **literal command** `echo hello` from the other user's terminal.

You can enclose **complex bash commands** in single quotes, and run them: 

```bash
hj tty002 echo 'hello ;  x=150; echo $x; x=$( date ); echo "$x"
```

... _carraige returns are accepatble here:_

```bash
hj tty002 echo 'hello
  x=150
  echo $x
  x=$( date )
  echo "$x"'
```

Produces the exact same output.

#### **Sending Signals**

For example:
- `:br` Send `SIGINT` (`Ctrl+C`)
- `:d` Send `SIGEND` (`Ctrl+D`)
- `:\n` Hit `Enter` on the Terminal
- `:logout` Send both SIGINT and SIGEND on the user's terminal, then kill the user's process.

Sent by:

```hj ttys002 :br```

### Reporting bugs / feature requests:

Please use this repository's issue tracking to report any issues or feature requests.




