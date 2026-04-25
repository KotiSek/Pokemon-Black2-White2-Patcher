import ndspy.narc


class ChallengeModePatcher:
    TR_NARC = 'a/0/9/1'
    PK_NARC = 'a/0/9/2'

    # Normal ID → Challenge ID
    LEADER_MAP = {
        # Gym Leaders
        156: 764,   # Cheren
        157: 765,   # Roxie
        154: 766,   # Burgh
        153: 767,   # Elesa
        158: 768,   # Clay
        155: 769,   # Skyla
        159: 770,   # Drayden
        160: 771,   # Marlon

        # Elite Four
        143: 772,   # Shauntal
        144: 774,   # Grimsley
        145: 773,   # Caitlin
        146: 775,   # Marshal

        # Champion
        536: 776,   # Iris
    }

    # IV boost dla zwykłych trenerów
    IV_BOOST = {
        0: 50,
        50: 100,
        100: 150,
        150: 200,
        200: 250,
        250: 250,
    }

    def _load_narc(self, rom, path):
        data = rom.rom.getFileByName(path)
        narc = ndspy.narc.NARC.__new__(ndspy.narc.NARC)
        narc._initFromData(data)
        return narc

    def _pk_size(self, flags):
        size = 8
        if flags & 1:
            size += 2
        if flags & 2:
            size += 8
        return size

    def enable(self, rom, log_fn=print):
        try:
            narc_tr = self._load_narc(rom, self.TR_NARC)
            narc_pk = self._load_narc(rom, self.PK_NARC)
        except Exception as e:
            log_fn(f"BŁĄD: Nie można otworzyć danych trenerów: {e}")
            return False

        # --- KROK 1: Boost poziomów i IV ---
        count_buffed = 0

        for idx in range(len(narc_tr.files)):
            tr = narc_tr.files[idx]

            if len(tr) < 4:
                continue

            pk = bytearray(narc_pk.files[idx])
            flags = tr[0]
            count = tr[3]
            size = self._pk_size(flags)

            if len(pk) == 0:
                continue

            changed = False

            for i in range(count):
                off = i * size
                if off + size > len(pk):
                    break

                # --- LEVEL SCALING ---
                level = int.from_bytes(pk[off + 2:off + 4], 'little')

                if 0 < level < 100:
                    if level <= 20:
                        boost = 1
                    elif level <= 30:
                        boost = 2
                    elif level <= 45:
                        boost = 3
                    else:
                        boost = 4

                    new_level = min(100, level + boost)
                    pk[off + 2:off + 4] = new_level.to_bytes(2, 'little')
                    changed = True

                # --- IV BOOST ---
                iv = pk[off]
                new_iv = self.IV_BOOST.get(iv, iv)

                if new_iv != iv:
                    pk[off] = new_iv
                    changed = True

            if changed:
                narc_pk.files[idx] = bytes(pk)
                count_buffed += 1

        log_fn(f"✓ Zbuffowano {count_buffed} trenerów (+lvl scaling, boost IV)")

        # --- KROK 2: Podmiana liderów ---
        count_leaders = 0

        for normal_id, challenge_id in self.LEADER_MAP.items():
            if challenge_id >= len(narc_tr.files):
                log_fn(f"⚠ Challenge ID {challenge_id} poza zakresem")
                continue

            narc_tr.files[normal_id] = narc_tr.files[challenge_id]
            narc_pk.files[normal_id] = narc_pk.files[challenge_id]

            tr = narc_tr.files[normal_id]
            pk = narc_pk.files[normal_id]

            flags = tr[0]
            count = tr[3]
            size = self._pk_size(flags)

            levels = []

            for i in range(count):
                off = i * size
                if off + 6 > len(pk):
                    break

                lvl = int.from_bytes(pk[off + 2:off + 4], 'little')
                levels.append(lvl)

            log_fn(f"✓ Lider {normal_id} → {challenge_id} | {count} pkmn | lvl={levels}")
            count_leaders += 1

        log_fn(f"✓ Podmieniono {count_leaders} liderów/E4/Champion")

        # --- ZAPIS ---
        rom.rom.setFileByName(self.TR_NARC, narc_tr.save())
        rom.rom.setFileByName(self.PK_NARC, narc_pk.save())

        log_fn("✓ Challenge Mode zastosowany!")

        return True