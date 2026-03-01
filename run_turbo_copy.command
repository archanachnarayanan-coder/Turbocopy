#!/bin/bash
cd "$(dirname "$0")"
python3 turbo_copy.py 2>/dev/null || python turbo_copy.py
