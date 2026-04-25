# gui/app.py

import customtkinter as ctk
from tkinter import filedialog
import threading
from core.patcher import Patcher

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pokemon White 2 Patcher")
        self.geometry("650x750")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="Pokemon BW2 Patcher",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=15)

        # ROM
        frame_rom = ctk.CTkFrame(self)
        frame_rom.pack(fill='x', padx=20, pady=5)
        ctk.CTkLabel(frame_rom, text="ROM:").pack(side='left', padx=5)
        self.rom_entry = ctk.CTkEntry(frame_rom, width=400)
        self.rom_entry.pack(side='left', padx=5)
        ctk.CTkButton(frame_rom, text="Otworz", width=80,
                      command=self._open_rom).pack(side='left')

        # Patche
        frame_p = ctk.CTkFrame(self)
        frame_p.pack(fill='x', padx=20, pady=10)
        ctk.CTkLabel(frame_p, text="Patche",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)

        self.var_evos      = ctk.BooleanVar(value=True)
        # self.var_iv      = ctk.BooleanVar(value=True)  # TODO: IV patch do naprawy
        self.var_ev        = ctk.BooleanVar(value=True)
        self.var_shiny     = ctk.BooleanVar(value=True)
        self.var_challenge = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(frame_p,
                        text="Napraw ewolucje (wymiana→lvl34/item, Espeon/Umbreon→kamien)",
                        variable=self.var_evos).pack(anchor='w', padx=10, pady=2)

        # TODO: Not working properly to be fixed
        # ctk.CTkCheckBox(frame_p,
        #                 text="Max IV (31 we wszystkich statystykach)",
        #                 variable=self.var_iv).pack(anchor='w', padx=10, pady=2)

        ctk.CTkCheckBox(frame_p,
                        text="Zeruj EV yield (pokemony nie daja EV po walce)",
                        variable=self.var_ev).pack(anchor='w', padx=10, pady=2)

        ctk.CTkCheckBox(frame_p,
                        text="Challenge Mode (trudniejsza gra — wyzsi liderzy)",
                        variable=self.var_challenge).pack(anchor='w', padx=10, pady=2)

        # Shiny rate
        frame_shiny = ctk.CTkFrame(frame_p)
        frame_shiny.pack(fill='x', padx=10, pady=2)
        ctk.CTkCheckBox(frame_shiny, text="Shiny Rate  1/",
                        variable=self.var_shiny).pack(side='left')
        self.shiny_entry = ctk.CTkEntry(frame_shiny, width=80)
        self.shiny_entry.insert(0, "8192")
        self.shiny_entry.pack(side='left', padx=5)
        ctk.CTkLabel(frame_shiny, text="(oryginal: 8192)").pack(side='left')

        # Button
        ctk.CTkButton(self, text="▶  ZASTOSUJ PATCHE", height=45,
                      font=ctk.CTkFont(size=16, weight="bold"),
                      command=self._apply).pack(pady=15)

        # Log
        self.log_box = ctk.CTkTextbox(self, height=220)
        self.log_box.pack(fill='x', padx=20, pady=5)
        self.log_box.configure(state='disabled')

    def _open_rom(self):
        path = filedialog.askopenfilename(filetypes=[("NDS ROM", "*.nds")])
        if path:
            self.rom_entry.delete(0, 'end')
            self.rom_entry.insert(0, path)

    def _log(self, msg: str):
        self.log_box.configure(state='normal')
        self.log_box.insert('end', msg + '\n')
        self.log_box.see('end')
        self.log_box.configure(state='disabled')

    def _apply(self):
        rom_path = self.rom_entry.get().strip()
        if not rom_path:
            self._log("⚠ Wybierz plik ROM!")
            return

        try:
            shiny_val = int(self.shiny_entry.get() or 8192)
        except ValueError:
            self._log("⚠ Shiny rate musi byc liczba!")
            return

        options = {
            'fix_evos':         self.var_evos.get(),
            'max_ivs':          False,  # TODO: tymczasowo wyłączone — IV patch do naprawy
            # 'max_ivs':        self.var_iv.get(),
            'zero_evs':         self.var_ev.get(),
            'challenge_mode':   self.var_challenge.get(),
            'shiny_rate':       self.var_shiny.get(),
            'shiny_rate_value': shiny_val,
        }

        self.log_box.configure(state='normal')
        self.log_box.delete('1.0', 'end')
        self.log_box.configure(state='disabled')

        threading.Thread(target=self._run_patch,
                         args=(rom_path, options), daemon=True).start()

    def _run_patch(self, rom_path, options):
        try:
            patcher = Patcher(rom_path, log_fn=self._log)
            patcher.apply(options)
        except Exception as e:
            self._log(f"BLAD KRYTYCZNY: {e}")

if __name__ == '__main__':
    app = App()
    app.mainloop()