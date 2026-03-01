# TurboCopy

A cross-platform GUI for copying large numbers of files with fast transfers and progress display.

- **Windows**: Uses Robocopy (multithreaded)
- **macOS / Linux**: Uses rsync (built-in on Mac)

## Download

**[Download latest release](releases)** — No Python required.

- **Windows**: `TurboCopy.exe`
- **macOS**: `TurboCopy` (build on Mac required)

## Features

- **Browse** source and destination folders
- **Fast copy** – Robocopy (Windows) or rsync (Mac/Linux)
- **Real-time progress** – see files as they're being copied
- **Scrollable console** – view full paths of all files copied
- **Completion confirmation** – popup when copy finishes
- **Stop button** – cancel an in-progress copy
- **Detailed log** – full output saved to copy_log.txt

## Requirements

- **Windows**: Python 3.6+ (tkinter included), Robocopy (built-in)
- **macOS / Linux**: Python 3.6+ (tkinter included), rsync (built-in on Mac; on Linux: `sudo apt install rsync`)

## Building a Standalone Executable (No Python Required)

Build a standalone app so users don't need to install Python:

```bash
python build.py
```

The output goes to `dist/` — `TurboCopy.exe` (Windows) or `TurboCopy` (Mac). Users can run it without Python.


## How to Run

```bash
python turbo_copy.py
```

**Windows**: Double-click `run_turbo_copy.bat`.

**macOS**: Double-click `run_turbo_copy.command` (first time: right-click → Open).

## Usage

1. Click **Browse...** next to Source Folder and select the folder to copy from
2. Click **Browse...** next to Destination Folder and select where to copy to
3. Optionally uncheck "Copy subdirectories (including empty)" if you only want top-level files
4. Click **Start Copy**
5. Watch the progress and file list as files are copied
6. A confirmation message appears when the copy completes
