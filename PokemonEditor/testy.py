from core.nds_reader import NDSRom

ROM_PATH = r"C:\Users\Kotik\Desktop\emulatory\ds\games\PK WHITE2\Pokemon - White Version 2 (USA, Europe) (NDSi Enhanced).nds"

def main():
    print("=== Dump ARM9 ===")

    try:
        rom = NDSRom(ROM_PATH)
        arm9 = rom.decompress_arm9()

        print(f"ARM9 size: {len(arm9)} bytes")

        start = 0x18E04
        end   = 0x18E40

        data = arm9[start:end]

        print(f"\nDump 0x{start:X} - 0x{end:X}:")
        print(data.hex())

        # czytelniejszy widok (co 2 bajty)
        print("\nThumb (2-byte chunks):")
        for i in range(0, len(data), 2):
            chunk = data[i:i+2]
            addr = start + i
            print(f"0x{addr:08X}: {chunk.hex()}")

    except Exception as e:
        print(f"BŁĄD: {e}")

if __name__ == "__main__":
    main()