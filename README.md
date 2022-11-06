## hijack

---

Inject input into another TTY

### Installation:

**On Linux**:

`sudo cp hijack.py /usr/bin/hj`

**On Mac**

```
mkdir -p /usr/local/bin
sudo cp hijack.py /usr/local/bin/hj
```

### Usage:

**List hijackable  ttys**:
```
tty list
```
**Run a commmand on `<tty>`:**

```bash
hj <tty> <command> [ -s/--strip]
```

### Shortcuts

| shortcut   | description                 |
|------------|-----------------------------
| ```:br```  | send break                  |
| ```:cr```  | send carriage return (\r\n) |
| ```:d```   |  send EOT (ctrl +d)         |
|```:logout```| logs this tty out (kills term)|
|```:cr``` | hit return |

