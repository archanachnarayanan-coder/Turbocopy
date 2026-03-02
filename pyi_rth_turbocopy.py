# Runtime hook: run before turbo_copy.py
# Suppress Tcl/Tk version warnings that can cause abort on Mac
import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'
