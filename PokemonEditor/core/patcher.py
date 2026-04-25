from core.nds_reader import NDSRom
from patches.evolutions import EvolutionPatcher
from patches.evs import EVPatcher
from patches.challenge_mode import ChallengeModePatcher
from patches.ivs_evs import IVPatcher
from patches.shiny_rate import ShinyRatePatcher


class Patcher:
    def __init__(self, rom_path: str, log_fn=print):
        self.log = log_fn
        self.rom = NDSRom(rom_path)
        self.evo_patcher       = EvolutionPatcher()
        self.ev_patcher        = EVPatcher()
        self.challenge_patcher = ChallengeModePatcher()
        self.iv_patcher        = IVPatcher()
        self.shiny_patcher     = ShinyRatePatcher()

    def apply(self, options: dict, output_path: str = None) -> str:
        self.log("=" * 50)
        self.log("=== Rozpoczynam patchowanie ===")
        self.log("=" * 50)

        results = {}

        # 1. Napraw ewolucje
        if options.get('fix_evos'):
            self.log("\n--- [1/7] Naprawianie ewolucji ---")
            results['fix_evos'] = self.evo_patcher.fix_all(self.rom, self.log)
        else:
            self.log("\n--- [1/7] Ewolucje: POMINIĘTO ---")
            results['fix_evos'] = None

        # 2. Max IV
        if options.get('max_ivs'):
            self.log("\n--- [2/7] Max IV patch ---")
            results['max_ivs'] = self.iv_patcher.apply_max_ivs(self.rom, self.log)
        else:
            self.log("\n--- [2/7] Max IV: POMINIĘTO ---")
            results['max_ivs'] = None

        # 3. Zerowanie EV yield
        if options.get('zero_evs'):
            self.log("\n--- [3/7] Zerowanie EV yield ---")
            results['zero_evs'] = self.ev_patcher.zero_ev_yields(self.rom, self.log)
        else:
            self.log("\n--- [3/7] EV yield: POMINIĘTO ---")
            results['zero_evs'] = None

        # 4. Challenge Mode
        if options.get('challenge_mode'):
            self.log("\n--- [4/7] Challenge Mode ---")
            results['challenge_mode'] = self.challenge_patcher.enable(self.rom, self.log)
        else:
            self.log("\n--- [4/7] Challenge Mode: POMINIĘTO ---")
            results['challenge_mode'] = None

        # 5. Shiny rate
        if options.get('shiny_rate'):
            rate = options.get('shiny_rate_value', 8192)
            self.log(f"\n--- [5/7] Shiny Rate -> 1/{rate} ---")
            results['shiny_rate'] = self.shiny_patcher.set_rate(self.rom, rate, self.log)
        else:
            self.log("\n--- [5/7] Shiny Rate: POMINIĘTO ---")
            results['shiny_rate'] = None

        # 6. (usunięto: Level Cap)
        # 7. (usunięto: Starter Items)

        # Podsumowanie
        self.log("\n" + "=" * 50)
        self.log("=== PODSUMOWANIE PATCHY ===")
        labels = {
            'fix_evos':       'Ewolucje',
            'max_ivs':        'Max IV',
            'zero_evs':       'Zerowanie EV',
            'challenge_mode': 'Challenge Mode',
            'shiny_rate':     'Shiny Rate',
        }
        errors = 0
        for key, label in labels.items():
            val = results.get(key)
            if val is None:
                self.log(f"  -  {label}: pominięto")
            elif val:
                self.log(f"  OK {label}: sukces")
            else:
                self.log(f"  !! {label}: BLAD!")
                errors += 1

        self.log("\n--- Zapisywanie pliku... ---")
        out = self.rom.save(output_path)

        self.log("=" * 50)
        if errors == 0:
            self.log("✓ Patchowanie zakonczone SUKCESEM!")
        else:
            self.log(f"⚠ Patchowanie z {errors} bledem/bledami — sprawdz logi powyzej!")
        self.log(f"Plik: {out}")
        self.log("=" * 50)
        return out
