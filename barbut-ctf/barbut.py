from pwn import *
import time

HOST = "10.213.0.102"
PORT = 44204

# Implementare corectă a LCG pentru glibc rand()
class GlibcRandom:
    def __init__(self):
        self.state = 0
    
    def srand(self, seed):
        self.state = seed
    
    def rand(self):
        # Algoritmul LCG din glibc
        self.state = ((self.state * 1103515245) + 12345) & 0x7fffffff
        return self.state

def test_seed(seed):
    """Testează ce număr generează un seed"""
    rng = GlibcRandom()
    rng.srand(seed)
    result = rng.rand() % 60 + 1
    return result

def find_seeds_for_target(target_min=55, target_max=60, max_seeds=500):
    """Găsește seed-uri care generează numere în intervalul dorit"""
    good_seeds = []
    
    # Căutăm în primul milion de seed-uri
    for seed in range(1, 1000000):
        value = test_seed(seed)
        if target_min <= value <= target_max:
            good_seeds.append((seed, value))
            if len(good_seeds) >= max_seeds:
                break
    
    return good_seeds

def exploit():
    print("[*] Căutăm seed-uri optime...")
    
    # Găsește seed-uri care generează valori mari (55-60)
    good_seeds = find_seeds_for_target(55, 60, 100)
    print(f"[+] Găsite {len(good_seeds)} seed-uri bune")
    
    if len(good_seeds) < 27:
        print("[!] Nu am găsit suficiente seed-uri bune!")
        return False
    
    # Afișează primele câteva
    print("[*] Primele 10 seed-uri:")
    for seed, value in good_seeds[:10]:
        print(f"    Seed {seed:6d} -> valoare {value}")
    
    try:
        p = remote(HOST, PORT)
        
        # Primește mesajele inițiale
        p.recvuntil(b"flag\n")
        
        wins = 0
        
        for round_num in range(27):
            print(f"\n[*] Runda {round_num + 1}/27")
            
            try:
                # Primește "Choose your lucky number"
                p.recvuntil(b"Choose your lucky number\n")
                
                # Folosește un seed bun (ciclic)
                seed = good_seeds[round_num % len(good_seeds)][0]
                expected_value = good_seeds[round_num % len(good_seeds)][1]
                print(f"[*] Seed: {seed} (așteptăm valoare ~{expected_value})")
                
                p.sendline(str(seed).encode())
                
                # Primește "Ready?"
                p.recvuntil(b"Ready?\n")
                
                # Răspunde "yes"
                p.sendline(b"yes")
                
                # Citește rezultatul
                result_line = p.recvline().decode().strip()
                print(f"[*] {result_line}")
                
                # Parsează rezultatul pentru a vedea valorile
                if "Computer choice:" in result_line:
                    parts = result_line.split(",")
                    if len(parts) >= 2:
                        comp_hex = parts[0].split(":")[-1].strip()
                        player_val = parts[1].split(":")[-1].strip()
                        try:
                            comp_dec = int(comp_hex, 16)
                            print(f"[*] Computer: {comp_dec} (0x{comp_hex}), Player: {player_val}")
                        except:
                            pass
                
                # Verifică rezultatul
                outcome = p.recvline().decode().strip()
                print(f"[*] {outcome}")
                
                if "win" in outcome.lower():
                    wins += 1
                    print(f"[+] Victorii: {wins}/25")
                else:
                    print(f"[-] Înfrângeri: {round_num + 1 - wins}")
                    
            except EOFError:
                print("[!] Conexiunea s-a închis prematur")
                break
        
        # Încearcă să primești flag-ul
        print(f"\n[*] Total victorii: {wins}/25")
        
        try:
            flag = p.recvall(timeout=3).decode()
            print(f"\n{'='*60}")
            print(f"[+] REZULTAT FINAL:")
            print(flag)
            print(f"{'='*60}")
            
            if "CTF{" in flag or "FLAG{" in flag or wins >= 25:
                p.close()
                return True
        except:
            print("[-] Nu s-a primit flag")
        
        p.interactive()
        p.close()
        
    except Exception as e:
        print(f"[!] Eroare: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = False
    attempts = 0
    max_attempts = 5
    
    while not success and attempts < max_attempts:
        attempts += 1
        print(f"\n{'='*60}")
        print(f"[*] Încercare {attempts}/{max_attempts}")
        print(f"{'='*60}\n")
        
        success = exploit()
        
        if not success and attempts < max_attempts:
            print("\n[*] Reîncerc în 2 secunde...")
            time.sleep(2)
    
    if success:
        print("\n[+] EXPLOIT REUȘIT!")
    else:
        print("\n[-] Exploit eșuat după toate încercările")