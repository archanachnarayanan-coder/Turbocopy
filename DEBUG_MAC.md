# Debugging TurboCopy.app Crash on Mac

## "macOS 26 required, have instead 16" Error

Your Python was built for a newer macOS than you're running. **Fix: Build with Python 3.11** (not 3.13).

1. Install Python 3.11 from https://www.python.org/downloads/release/python-3119/
2. Use it to build:
   ```bash
   python3.11 -m pip install pyinstaller
   python3.11 -m PyInstaller --noconfirm turbo_copy_mac.spec
   ```
3. The resulting TurboCopy.app should run on your Mac.

---

## Step 0: Test if Python version works

```bash
cd ~/Turbocopy
python3 turbo_copy.py
```

If this works, the issue is with the PyInstaller build. If it crashes too, the issue is in the code or your Python/tkinter setup.

## Step 1: Build a debug version (shows errors)

```bash
cd ~/Turbocopy
git pull
python3 build.py --debug
```

This creates a debug build. When you run it, a **Terminal window opens** with the app — any crash or error will appear there.

Run it:
```bash
open dist/TurboCopy.app
```
Or double-click. Watch the Terminal window for the error message.

## Step 2: Or run the binary directly

```bash
cd dist
./TurboCopy.app/Contents/MacOS/TurboCopy
```

The error will print in the terminal. **Copy the full error and share it** so we can fix it.

## Step 3: Check the crash log
1. Open **Console** app (Applications → Utilities)
2. Select your Mac in the sidebar
3. Search for "TurboCopy" or look in **Crash Reports**
4. The crash log shows the exact error

**Common causes:**
- **Intel vs Apple Silicon**: Build on the same Mac type you're running (M1/M2 on Apple Silicon, or Intel). You can't run an Intel build on M1 without Rosetta.
- **Python version**: Ensure you built with a standard Python (python.org or Homebrew), not a minimal or managed install.
