import ndspy.narc

class EvolutionPatcher:
    NARC_PATH = 'a/0/1/9'

    # --- Typy ewolucji ---
    EVO_LEVEL_UP        = 0x04
    EVO_TRADE_PLAIN     = 0x05
    EVO_TRADE_ITEM      = 0x06
    EVO_USE_STONE       = 0x08
    EVO_LEVEL_ITEM_ANY  = 0x17  # level up trzymając item (dowolna pora)
    EVO_LEVEL_ITEM_DAY  = 0x18  # level up trzymając item w dzień
    EVO_LEVEL_ITEM_NGHT = 0x19  # level up trzymając item w nocy
    EVO_FRIEND_ANY      = 0x01
    EVO_FRIEND_DAY      = 0x02
    EVO_FRIEND_NIGHT    = 0x03
    EVO_LEVEL_ITEM_NGHT2= 0x10  # level up z itemem w nocy (Feebas beauty)

    # --- ID przedmiotów w BW2 ---
    SUN_STONE_ID        = 80    # Sun Stone
    MOON_STONE_ID       = 81    # Moon Stone
    THUNDER_STONE_ID    = 83    # Thunder Stone
    PRISM_SCALE_ID      = 537   # Prism Scale (Feebas → Milotic)

    # --- Konkretne reguły dla każdego pokémona ---
    # Format: pokemon_id → lista (slot_wynik_id, nowy_typ, nowy_arg)
    # None w nowy_arg oznacza "zachowaj oryginalny arg"
    SPECIFIC_RULES = {
        # Wymiana BEZ przedmiotu → poziom 34
        64:  [(65,  EVO_LEVEL_UP, 34)],   # Kadabra → Alakazam
        67:  [(68,  EVO_LEVEL_UP, 34)],   # Machoke → Machamp
        75:  [(76,  EVO_LEVEL_UP, 34)],   # Graveler → Golem
        93:  [(94,  EVO_LEVEL_UP, 34)],   # Haunter → Gengar
        525: [(526, EVO_LEVEL_UP, 34)],   # Boldore → Gigalith
        533: [(534, EVO_LEVEL_UP, 34)],   # Gurdurr → Conkeldurr

        # Wymiana Z przedmiotem → level up trzymając ten sam przedmiot
        61:  [(186, EVO_LEVEL_ITEM_ANY, None)],  # Poliwhirl → Politoed (King's Rock)
        79:  [(199, EVO_LEVEL_ITEM_ANY, None)],  # Slowpoke → Slowking (King's Rock)
        95:  [(208, EVO_LEVEL_ITEM_ANY, None)],  # Onix → Steelix (Metal Coat)
        112: [(464, EVO_LEVEL_ITEM_ANY, None)],  # Rhydon → Rhyperior (Protector)
        117: [(230, EVO_LEVEL_ITEM_ANY, None)],  # Seadra → Kingdra (Dragon Scale)
        123: [(212, EVO_LEVEL_ITEM_ANY, None)],  # Scyther → Scizor (Metal Coat)
        125: [(466, EVO_LEVEL_ITEM_ANY, None)],  # Electabuzz → Electivire (Electirizer)
        126: [(467, EVO_LEVEL_ITEM_ANY, None)],  # Magmar → Magmortar (Magmarizer)
        137: [(233, EVO_LEVEL_ITEM_ANY, None)],  # Porygon → Porygon2 (Up-Grade)
        233: [(474, EVO_LEVEL_ITEM_ANY, None)],  # Porygon2 → Porygon-Z (Dubious Disc)
        356: [(477, EVO_LEVEL_ITEM_ANY, None)],  # Dusclops → Dusknoir (Reaper Cloth)
        366: [(367, EVO_LEVEL_ITEM_ANY, None), (368, EVO_LEVEL_ITEM_ANY, None)],  # Clamperl → Huntail + Gorebyss
        # Eevee → Espeon (Sun Stone), Umbreon (Moon Stone)
        133: [(196, EVO_USE_STONE, SUN_STONE_ID),   # Espeon
              (197, EVO_USE_STONE, MOON_STONE_ID)],  # Umbreon

        # Magneton/Nosepass → Thunder Stone
        82:  [(462, EVO_USE_STONE, THUNDER_STONE_ID)],  # Magneton → Magnezone
        299: [(476, EVO_USE_STONE, THUNDER_STONE_ID)],  # Nosepass → Probopass

        # Chingling → Chimecho: przyjaźń noc → poziom 30
        433: [(358, EVO_LEVEL_UP, 30)],

        # Feebas → Milotic: level up trzymając Prism Scale
        349: [(350, EVO_LEVEL_ITEM_ANY, PRISM_SCALE_ID)],
    }

    def _load_narc(self, rom):
        data = rom.get_file(self.NARC_PATH)
        narc = ndspy.narc.NARC.__new__(ndspy.narc.NARC)
        narc._initFromData(data)
        return narc

    def _save_narc(self, rom, narc):
        rom.rom.setFileByName(self.NARC_PATH, narc.save())

    def fix_all(self, rom, log_fn=print):
        try:
            narc = self._load_narc(rom)
        except Exception as e:
            log_fn(f"BŁĄD: Nie można otworzyć pliku ewolucji: {e}")
            return False

        count = 0

        for pokemon_id, rules in self.SPECIFIC_RULES.items():
            if pokemon_id >= len(narc.files):
                continue

            entry = bytearray(narc.files[pokemon_id])

            for (target_result, new_type, new_arg) in rules:
                # Znajdź slot który prowadzi do target_result
                matched = False
                for slot in range(7):
                    offset = slot * 6
                    if offset + 6 > len(entry):
                        break

                    evo_type   = int.from_bytes(entry[offset:offset+2], 'little')
                    evo_result = int.from_bytes(entry[offset+4:offset+6], 'little')

                    if evo_result == target_result and evo_type != 0:
                        old_arg = int.from_bytes(entry[offset+2:offset+4], 'little')
                        arg_to_use = old_arg if new_arg is None else new_arg

                        entry[offset:offset+2]   = new_type.to_bytes(2, 'little')
                        entry[offset+2:offset+4] = arg_to_use.to_bytes(2, 'little')

                        log_fn(f"  ✓ ID {pokemon_id} → ID {target_result} | "
                               f"typ: 0x{evo_type:02X}→0x{new_type:02X} | "
                               f"arg: {old_arg}→{arg_to_use}")
                        count += 1
                        matched = True
                        break

                if not matched:
                    log_fn(f"  ⚠ Nie znaleziono ewolucji ID {pokemon_id} → ID {target_result}")

            narc.files[pokemon_id] = bytes(entry)

        self._save_narc(rom, narc)
        log_fn(f"\n✓ Łącznie naprawiono {count} ewolucji")
        return True