"""Build TurboCopy into a standalone executable. Run: python build.py"""
import subprocess
import sys

def main():
    print("Installing PyInstaller if needed...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"], check=False)
    print("Building TurboCopy...")
    result = subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "turbo_copy.spec"])
    if result.returncode == 0:
        print("\nBuild complete! Output is in: dist/")
        print("  Windows: dist/TurboCopy.exe")
        print("  Mac:     dist/TurboCopy")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
