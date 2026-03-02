"""Build TurboCopy into a standalone executable. Run: python build.py"""
import platform
import subprocess
import sys

def main():
    print("Installing PyInstaller if needed...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"], check=False)
    print("Building TurboCopy...")

    is_mac = platform.system() == "Darwin"
    debug = "--debug" in sys.argv

    if is_mac:
        spec = "turbo_copy_mac_debug.spec" if debug else "turbo_copy_mac.spec"
        if debug:
            print("DEBUG MODE: Build will show a Terminal window with errors when app runs.")
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--noconfirm",
            spec
        ])
        if result.returncode == 0:
            print("\nBuild complete! Output is in: dist/TurboCopy.app")
            print("  Zip TurboCopy.app and upload to GitHub. Users unzip and double-click.")
    else:
        # Windows: Use existing spec (onefile .exe)
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "turbo_copy.spec"])
        if result.returncode == 0:
            print("\nBuild complete! Output is in: dist/TurboCopy.exe")

    if result.returncode != 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
