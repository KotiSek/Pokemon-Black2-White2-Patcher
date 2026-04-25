# Pokemon BW2 Patcher

Narzędzie do patchowania ROM-u **Pokemon White 2 (NDS)** z graficznym interfejsem (CustomTkinter).

## Dostępne patche

| Patch | Opis |
|---|---|
| Napraw ewolucje | Wymiana → lvl 34 lub item; Espeon/Umbreon → kamień |
| Max IV | Ustawia 31 we wszystkich statystykach |
| Zeruj EV yield | Pokémony nie dają EV po walce |
| Challenge Mode | Trudniejsza gra — wyżsi liderzy |
| Shiny Rate | Zmiana szansy na shiny (domyślnie 1/8192) |
| Level Cap | Capy poziomów wg liczby odznak |
| Starter Items | Start z 999× Rare Candy w ekwipunku |

## Wymagania

- Python 3.10+
- Zależności:

```bash
pip install -r requirements.txt
```

## Uruchomienie

```bash
python main.py
```

W oknie aplikacji:
1. Kliknij **Otwórz** i wskaż plik `.nds` z ROM-em
2. Zaznacz patche, które chcesz zastosować
3. Kliknij **ZASTOSUJ PATCHE**
4. Patchowany plik zostanie zapisany jako `<oryginalna_nazwa>.patched.nds` w tym samym folderze

## Diagnostyka ARM9 (dla deweloperów)

```bash
python testy.py <ścieżka_do_romu.nds>
```

## Ważne

> ROM-y gier Nintendo są chronione prawem autorskim.  
> To narzędzie służy wyłącznie do modyfikacji posiadanych przez Ciebie kopii zapasowych.  
> Pliki `.nds` **nie są** i **nie powinny być** przesyłane do repozytorium.
