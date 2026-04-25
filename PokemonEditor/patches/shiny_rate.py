class ShinyRatePatcher:


    OFFSET_CMP = 0x00018E1C
    OFFSET_EOR = 0x00018E1A

    EXPECTED = bytes([
        0x08, 0x28,
        0x01, 0xD2,
        0x01, 0x20,
        0x70, 0x47,
        0x00, 0x20,
        0x70, 0x47
    ])

    def set_rate(self, rom, rate: int, log_fn=print):
        try:
            arm9 = bytearray(rom.decompress_arm9())

            threshold = round(65536 / rate)
            log_fn(f"Target: 1/{rate} (threshold={threshold})")

            #  CMP
           
            if threshold <= 255:
                current = bytes(arm9[self.OFFSET_CMP:self.OFFSET_CMP+12])

                if current != self.EXPECTED:
                    log_fn("❌ ROM niezgodny — anuluję")
                    return False

                arm9[self.OFFSET_CMP:self.OFFSET_CMP+2] = bytes([
                    threshold, 0x28
                ])

                rom.compress_and_set_arm9(bytes(arm9))

                real = round(65536 / threshold)
                log_fn(f"✅ Dokładny shiny: 1/{real}")
                return True

                #Fallback
            else:
                import math

                shift = int(math.log2(8192 / rate))
                if shift < 0:
                    shift = 0
                if shift > 15:
                    shift = 15

                log_fn(f"Fallback RNG shift: {shift}")

                instr = 0x0800 | (shift << 6)
                arm9[self.OFFSET_EOR:self.OFFSET_EOR+2] = bytes([
                    instr & 0xFF,
                    instr >> 8
                ])

                rom.compress_and_set_arm9(bytes(arm9))

                approx = 8192 >> shift
                log_fn(f"⚠ Przybliżony shiny: ~1/{approx}")
                return True

        except Exception as e:
            log_fn(f"❌ Błąd: {e}")
            return False