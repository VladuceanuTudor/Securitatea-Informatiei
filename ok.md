fmtstr_payload(offset, {hook_addr: win_addr})
```

This creates a format string that:

1. **Places addresses on the stack**: Puts `hook_addr` (0x0804c024) at a specific stack position
2. **Uses `%n` to write**: Uses format string specifiers to write `win_addr` (0x080491b6) to the location pointed to by `hook_addr`

**Step by step:**
```
Before: hook (0x0804c024) contains → 0x0804925e (safe function)
After:  hook (0x0804c024) contains → 0x080491b6 (win function)
```

### 4. **Why it worked:**

When `offset` was correct (probably 4 or 6), the format string payload:
- Put the address `0x0804c024` on the stack
- Used `%n` writes to modify the value at that address
- Changed it from pointing to `safe()` to pointing to `win()`
- When `(*(code *)hook)()` executed, it called `win()` instead of `safe()`
- `win()` reads and prints the flag!

### **Visual Example:**
```
Stack before format string:
[...][0x0804c024][...][format specifiers]
      ↑ This is hook's address

Format string does:
%37302x     → Print 37302 characters (builds up byte count)
%4$n        → Write that count (37302 = 0x91b6) to 4th arg on stack
            → 4th arg is 0x0804c024 (hook's address)
            → So it writes 0x91b6 to hook

Result:
hook now points to 0x080491b6 (win function)