# Debugging TurboCopy.app Crash on Mac

If the app crashes on open, run it from Terminal to see the error:

```bash
# Go to the folder containing TurboCopy.app
cd ~/Downloads   # or wherever you extracted it

# Run and show any errors
./TurboCopy.app/Contents/MacOS/TurboCopy
```

The error message will appear in the terminal.

**Or check the crash log:**
1. Open **Console** app (Applications → Utilities)
2. Select your Mac in the sidebar
3. Search for "TurboCopy" or look in **Crash Reports**
4. The crash log shows the exact error

**Common causes:**
- **Intel vs Apple Silicon**: Build on the same Mac type you're running (M1/M2 on Apple Silicon, or Intel). You can't run an Intel build on M1 without Rosetta.
- **Python version**: Ensure you built with a standard Python (python.org or Homebrew), not a minimal or managed install.
