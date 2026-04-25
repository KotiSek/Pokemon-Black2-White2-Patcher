import ndspy.narc

class EVPatcher:
    NARC_PATH = 'a/0/1/6'

    # Offset 0x1C (28) = EV yield HP
    # Offset 0x1D (29) = EV yield Attack
    # Offset 0x1E (30) = EV yield Defense
    # Offset 0x1F (31) = EV yield Speed
    # Offset 0x20 (32) = EV yield Sp.Attack
    # Offset 0x21 (33) = EV yield Sp.Defense
    EV_OFFSET = 0x1C
    EV_COUNT  = 6

    def _load_narc(self, rom):
        data = rom.get_file(self.NARC_PATH)
        narc = ndspy.narc.NARC.__new__(ndspy.narc.NARC)
        narc._initFromData(data)
        return narc

    def zero_ev_yields(self, rom, log_fn=print):
        try:
            narc = self._load_narc(rom)
        except Exception as e:
            log_fn(f"BŁĄD: Nie można otworzyć Personal Data: {e}")
            return False

        count = 0
        for i, entry in enumerate(narc.files):
            data = bytearray(entry)
            if len(data) < self.EV_OFFSET + self.EV_COUNT:
                continue

            
            has_evs = any(data[self.EV_OFFSET + j] != 0 for j in range(self.EV_COUNT))
            if has_evs:
                for j in range(self.EV_COUNT):
                    data[self.EV_OFFSET + j] = 0
                narc.files[i] = bytes(data)
                count += 1

        rom.rom.setFileByName(self.NARC_PATH, narc.save())
        log_fn(f"✓ Wyzerowano EV yield u {count} pokémonów")
        return True