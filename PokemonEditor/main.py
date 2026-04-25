import sys
from pathlib import Path

# Upewniamy się, że katalog projektu jest w sys.path
# (pozwala uruchamiać skrypt spoza jego katalogu)
sys.path.insert(0, str(Path(__file__).parent))

from gui.app import App

if __name__ == '__main__':
    app = App()
    app.mainloop()
