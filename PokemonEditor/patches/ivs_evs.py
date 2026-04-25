# patches/ivs_evs.py
 """
class IVPatcher:
    
    Patch sprawia że każdy pokemon dostaje 31 IV we wszystkich statach.
    Zamieniamy MOV R1,#0x1F na MOV R0,#0xFF — po AND R0,R1 wynik to zawsze 0xFF & 0x1F = 31.
    Oryginalny flow funkcji (PUSH/POP stos) pozostaje nienaruszony.
    Zweryfikowany offset: 0x1E0FC (White 2 USA/EU, zdekompresowany ARM9).

    OFFSET_W2 = 0x0001E0FC

    # Oryginalne bajty: MOV R1,#0x1F + AND R0,R1
    ORIGINAL_BYTES = bytes([0x1F, 0x21, 0x08, 0x40])
 
    # MOV R0,#0xFF + AND R0,R1 => 0xFF & 0x1F = 31, flow funkcji nienaruszony
    PATCH_BYTES = bytes([0x1F, 0x20, 0x00, 0x46])  # MOV R0,#31 + MOV R0,R0 (NOP)

    def apply_max_ivs(self, rom, log_fn=print):
        try:
            arm9 = bytearray(rom.decompress_arm9())
            offset = self.OFFSET_W2

            if offset + 4 > len(arm9):
                log_fn(f"BŁĄD: Offset IV 0x{offset:X} poza zakresem ARM9 ({len(arm9)} bajtów)")
                return False

            original = bytes(arm9[offset:offset+4])
            log_fn(f"Bajty pod 0x{offset:X}: {original.hex()}")

            if original != self.ORIGINAL_BYTES:
                log_fn(f"BŁĄD: Oczekiwano {self.ORIGINAL_BYTES.hex()}, znaleziono {original.hex()}")
                log_fn("Offset prawdopodobnie nieprawidłowy dla tego ROM-u.")
                return False

            arm9[offset:offset+4] = self.PATCH_BYTES
            rom.compress_and_set_arm9(bytes(arm9))

            log_fn(f"✓ Max IV patch zastosowany @ 0x{offset:X} ({self.ORIGINAL_BYTES.hex()} → {self.PATCH_BYTES.hex()})")
            return True

        except Exception as e:
            log_fn(f"BŁĄD IV patch: {e}")
            return False
             
