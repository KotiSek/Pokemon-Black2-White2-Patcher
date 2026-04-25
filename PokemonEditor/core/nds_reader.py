import ndspy.rom
import ndspy.codeCompression
from pathlib import Path

class NDSRom:
    def __init__(self, path: str):
        self.path = Path(path)
        self.rom = ndspy.rom.NintendoDSRom.fromFile(str(path))
        
    def decompress_arm9(self):
        return ndspy.codeCompression.decompress(self.rom.arm9)

    def compress_and_set_arm9(self, data):
        # isArm9=True jest kluczowe dla poprawnych sum kontrolnych!
        self.rom.arm9 = ndspy.codeCompression.compress(data, isArm9=True)

    def get_file(self, path: str) -> bytes:
        return self.rom.getFileByName(path)

    def save(self, output_path: str = None):
        out = output_path or str(self.path.with_suffix('.patched.nds'))
        # NIE wyłączamy kompresji - NDSi Enhanced tego nie lubi
        self.rom.saveToFile(out)
        return out