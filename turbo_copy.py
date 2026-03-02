"""
TurboCopy - Fast multithreaded file copy with progress display.
Windows: Uses Robocopy. macOS/Linux: Uses rsync.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import queue
import os
import sys
import re
import platform
from datetime import datetime

IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"


class TurboCopyGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TurboCopy")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)

        # Soft Neutrals (white, light gray, charcoal)
        self.bg_color = "#FFFFFF"       # White
        self.light_gray = "#FFFAFA"     # Light gray
        self.charcoal = "#4A4A4A"       # Charcoal
        self.text_color = self.charcoal
        self.root.configure(bg=self.bg_color)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TButton", background=self.charcoal, foreground="white", padding=(8, 4))
        self.style.map("TButton", background=[("active", "#5A5A5A")])
        self.very_light_grey = "#FAFAFA"
        self.style.configure("TEntry", fieldbackground=self.very_light_grey, foreground=self.charcoal)
        self.style.configure("TCheckbutton", background=self.bg_color, foreground=self.text_color)
        self.style.configure("Vertical.TScrollbar", troughcolor="#E8E8E8", background="#B0B0B0")
        # Use system fonts on Mac (Segoe UI/Consolas are Windows-only)
        self.font_ui = "Segoe UI" if IS_WINDOWS else "Helvetica Neue"
        self.font_mono = "Consolas" if IS_WINDOWS else "Menlo"
        self.style.map("Vertical.TScrollbar", background=[("active", "#4A4A4A")])

        self.setup_ui()
        self.copy_process = None
        self.output_queue = queue.Queue()
        self.is_copying = False
        self.cancelled = False
        self.log_file = None
        self.files_copied = 0
        self.total_files = None

    def setup_ui(self):
        """Build the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="15 15 15 15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Source section
        ttk.Label(main_frame, text="Source Folder:", font=(self.font_ui, 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.source_var = tk.StringVar()
        source_frame = ttk.Frame(main_frame)
        source_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        source_frame.columnconfigure(0, weight=1)

        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_var, width=60)
        self.source_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ttk.Button(source_frame, text="Browse...", command=self.browse_source).grid(row=0, column=1)

        # Destination section
        ttk.Label(main_frame, text="Destination Folder:", font=(self.font_ui, 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.dest_var = tk.StringVar()
        dest_frame = ttk.Frame(main_frame)
        dest_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        dest_frame.columnconfigure(0, weight=1)

        self.dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_var, width=60)
        self.dest_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ttk.Button(dest_frame, text="Browse...", command=self.browse_destination).grid(row=0, column=1)

        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=4, column=0, sticky="w", pady=(0, 15))

        self.copy_subdirs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Copy subdirectories (including empty)",
            variable=self.copy_subdirs_var,
        ).pack(side=tk.LEFT, padx=(0, 20))

        # Progress / Status
        ttk.Label(main_frame, text="Copy Progress:", font=(self.font_ui, 10, "bold")).grid(
            row=5, column=0, sticky=tk.W, pady=(0, 5)
        )

        # Progress display - shows "X of Y files processed"
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=6, column=0, sticky="nsew", pady=(0, 15))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)

        self.progress_var = tk.StringVar(value="Waiting to start...")
        self.progress_label = ttk.Label(
            progress_frame,
            textvariable=self.progress_var,
            font=(self.font_ui, 14, "bold"),
            wraplength=600,
        )
        self.progress_label.pack(anchor=tk.W, pady=(0, 5))

        # Console - scrollable list of files being copied
        ttk.Label(progress_frame, text="Files copied:", font=(self.font_ui, 9, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.console_frame = tk.Frame(progress_frame)
        self.console_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.cons_y = ttk.Scrollbar(self.console_frame, orient=tk.VERTICAL)
        self.console = tk.Text(
            self.console_frame,
            height=12,
            font=(self.font_mono, 9),
            bg=self.very_light_grey,
            fg=self.charcoal,
            insertbackground=self.text_color,
            wrap=tk.WORD,
            yscrollcommand=self.cons_y.set,
        )
        self.cons_y.config(command=self.console.yview)
        self.console.config(yscrollcommand=self.cons_y.set)
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.console.config(state=tk.DISABLED)
        self.console_line_limit = 10000

        self.log_path_var = tk.StringVar(value="")
        self.log_path_label = tk.Label(
            progress_frame,
            textvariable=self.log_path_var,
            font=(self.font_ui, 9),
            fg=self.charcoal,
            bg=self.bg_color,
            wraplength=600,
        )
        self.log_path_label.pack(anchor=tk.W)

        # Status bar
        self.status_var = tk.StringVar(value="Ready. Select source and destination folders, then click Copy.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=7, column=0, sticky="ew", pady=(10, 0))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, pady=(15, 0))

        self.copy_btn = ttk.Button(button_frame, text="Start Copy", command=self.start_copy, padding=(20, 10))
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_copy, state=tk.DISABLED, padding=(20, 10))
        self.stop_btn.pack(side=tk.LEFT)

    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_var.set(folder)

    def browse_destination(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_var.set(folder)

    def _is_file_copy_line(self, line):
        """Check if output line indicates a file was copied."""
        line_lower = line.lower()
        if IS_WINDOWS:
            return any(
                x in line_lower
                for x in ("new file", "newer", "older", "same", "extra", "lonely", "tweaked")
            )
        else:
            # rsync -v: each file is a line, skip summary/stats lines
            stripped = line.strip()
            if not stripped or stripped.startswith("total size") or stripped.startswith("sent ") or "speedup" in stripped:
                return False
            return "/" in stripped or "." in stripped or len(stripped) > 2

    def _extract_filename(self, line, full_path=False):
        """Extract filename/path from copy output line."""
        if IS_WINDOWS:
            match = re.search(r"\d+\s+(.+)$", line.strip())
            if match:
                path = match.group(1).strip()
                if full_path:
                    return path
                return path if len(path) <= 80 else path[:77] + "..."
            for part in reversed(line.split()):
                if part and ("\\" in part or "/" in part or "." in part):
                    return part if full_path else ((part[:77] + "...") if len(part) > 80 else part)
        else:
            # rsync: line is the path
            path = line.strip().rstrip("/")
            if not path:
                return ""
            if full_path:
                return path
            return path if len(path) <= 80 else path[:77] + "..."
        return ""

    def _parse_summary(self, line):
        """Parse 'Files : Total Copied Skipped...' summary line."""
        match = re.search(r"Files\s*:\s*(\d+)\s+(\d+)\s+(\d+)", line, re.IGNORECASE)
        if match:
            return int(match.group(1)), int(match.group(2)), int(match.group(3))
        return None, None, None

    def start_copy(self):
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()

        if not source:
            messagebox.showerror("Error", "Please select a source folder.")
            return
        if not dest:
            messagebox.showerror("Error", "Please select a destination folder.")
            return
        if not os.path.isdir(source):
            messagebox.showerror("Error", f"Source folder does not exist:\n{source}")
            return

        self.is_copying = True
        self.cancelled = False
        self.files_copied = 0
        self.total_files = None
        self.copy_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("Counting files...")
        self.progress_var.set("Scanning source folder...")
        self.cons_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.insert(tk.END, "Counting files...\n")
        self.console.config(state=tk.DISABLED)

        source_folder_name = os.path.basename(source.rstrip(os.sep))
        effective_dest = os.path.join(dest, source_folder_name)
        # Use writable dir: app bundle is read-only on Mac; Downloads may be read-only
        if getattr(sys, "frozen", False) and IS_MAC:
            log_dir = os.path.join(os.path.expanduser("~"), "Library", "Logs", "TurboCopy")
            os.makedirs(log_dir, exist_ok=True)
            self.log_file = os.path.join(log_dir, "copy_log.txt")
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.log_file = os.path.join(script_dir, "copy_log.txt")
        self.log_path_var.set(f"Log: {self.log_file}")

        def count_then_copy():
            total_count = 0
            for root, dirs, files in os.walk(source):
                if not self.is_copying:
                    return
                total_count += len(files)
                if total_count % 1000 == 0 and total_count > 0:
                    self.root.after(0, lambda n=total_count: self.progress_var.set(f"Found {n} files..."))
            if not self.is_copying:
                return
            self.total_files = total_count
            self.root.after(0, lambda: self._start_copy(source, effective_dest))

        threading.Thread(target=count_then_copy, daemon=True).start()
        self.poll_output()

    def _start_copy(self, source, effective_dest):
        """Called when file count is done - starts copy and updates UI."""
        self.status_var.set("Copying files...")
        if self.total_files is not None:
            self.progress_var.set(f"0 of {self.total_files} files processed...")
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.insert(tk.END, "Files being copied:\n")
        self.console.config(state=tk.DISABLED)
        threading.Thread(target=self._run_copy, args=(source, effective_dest), daemon=True).start()

    def _run_copy(self, source, dest):
        """Execute copy in a subprocess. Uses Robocopy on Windows, rsync on macOS/Linux."""
        if IS_WINDOWS:
            self._run_robocopy(source, dest)
        else:
            self._run_rsync(source, dest)

    def _run_robocopy(self, source, dest):
        """Windows: Use Robocopy."""
        cmd = [
            "robocopy",
            source,
            dest,
            "/MT:16",
            "/E",
            "/V",
            "/R:3",
            "/W:5",
        ]
        if not self.copy_subdirs_var.get():
            cmd.remove("/E")
            cmd.extend(["/S"])

        try:
            with open(self.log_file, "w", encoding="utf-8", errors="replace") as log:
                log.write(f"TurboCopy Log - {datetime.now().isoformat()}\n")
                log.write(f"Source: {source}\n")
                log.write(f"Destination: {dest}\n")
                log.write("-" * 60 + "\n\n")

                creation_flags = subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
                self.copy_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=creation_flags,
                )
                self._read_copy_output(source, log)
            self.output_queue.put(None)
        except Exception as e:
            self._handle_copy_error(e)

    def _run_rsync(self, source, dest):
        """macOS/Linux: Use rsync."""
        # Ensure trailing slash for rsync directory semantics (copy contents into dest)
        source_slash = source.rstrip("/") + "/"
        dest_slash = dest.rstrip("/") + "/"
        os.makedirs(dest, exist_ok=True)

        rsync_path = "/usr/bin/rsync" if IS_MAC else "rsync"  # Full path on Mac (PATH may be minimal in .app)
        cmd = [rsync_path, "-av"]
        if not self.copy_subdirs_var.get():
            cmd.extend(["--exclude=*/"])  # Top-level files only, no subdirectories

        try:
            with open(self.log_file, "w", encoding="utf-8", errors="replace") as log:
                log.write(f"TurboCopy Log - {datetime.now().isoformat()}\n")
                log.write(f"Source: {source_slash}\n")
                log.write(f"Destination: {dest_slash}\n")
                log.write("-" * 60 + "\n\n")

                self.copy_process = subprocess.Popen(
                    cmd + [source_slash, dest_slash],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    encoding="utf-8",
                    errors="replace",
                )
                self._read_copy_output(source, log)
            self.output_queue.put(None)
        except Exception as e:
            self._handle_copy_error(e)

    def _read_copy_output(self, source, log):
        """Read and parse copy process output (Robocopy or rsync)."""
        files_copied = 0
        for line in iter(self.copy_process.stdout.readline, ""):
            if not self.is_copying:
                break
            log.write(line)
            log.flush()
            if self._is_file_copy_line(line):
                files_copied += 1
                rel_path = self._extract_filename(line, full_path=True)
                if IS_WINDOWS:
                    full_path = os.path.normpath(os.path.join(source, rel_path)) if rel_path else rel_path
                else:
                    full_path = os.path.normpath(os.path.join(source.rstrip("/"), rel_path)) if rel_path else rel_path
                self.output_queue.put(("progress", files_copied, None, full_path))
            else:
                total, copied, skipped = self._parse_summary(line)
                if total is not None:
                    self.output_queue.put(("summary", total, copied, skipped))
        self.copy_process.wait()

    def _handle_copy_error(self, e):
        """Handle copy subprocess error."""
        try:
            with open(self.log_file, "a", encoding="utf-8", errors="replace") as log:
                log.write(f"ERROR: {e}\n")
        except OSError:
            pass
        self.output_queue.put(("error", str(e)))
        self.output_queue.put(None)

    def _append_to_console(self, text):
        """Append a line to the console and optionally trim old content."""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, text + "\n")
        self.console.see(tk.END)
        line_count = int(self.console.index("end-1c").split(".")[0])
        if line_count > self.console_line_limit:
            delete_to = line_count - self.console_line_limit + 1
            self.console.delete("1.0", f"{delete_to}.0")
        self.console.config(state=tk.DISABLED)

    def poll_output(self):
        """Poll the output queue and update progress."""
        latest_count = self.files_copied
        latest_total = self.total_files
        files_to_show = []
        done = False

        try:
            while True:
                item = self.output_queue.get_nowait()
                if item is None:
                    done = True
                    break
                if isinstance(item, tuple):
                    if item[0] == "progress":
                        latest_count = item[1]
                        if item[2] is not None:
                            latest_total = item[2]
                        if len(item) > 3 and item[3]:
                            files_to_show.append((item[1], item[2], item[3]))
                    elif item[0] == "summary":
                        latest_total = item[1]
                        latest_count = item[1]
                    elif item[0] == "error":
                        self.progress_var.set(f"Error: {item[1]}")
        except queue.Empty:
            pass

        for count, total, filename in files_to_show:
            prefix = f"  {count} of {total}  " if total is not None else "  "
            self._append_to_console(prefix + filename)

        if done:
            self.on_copy_complete()
            return

        self.files_copied = latest_count
        if latest_total is not None:
            self.total_files = latest_total
        if self.total_files is not None:
            self.progress_var.set(f"{self.files_copied} of {self.total_files} files processed")
        else:
            self.progress_var.set(f"{self.files_copied} files processed...")

        if self.is_copying:
            self.root.after(50, self.poll_output)

    def on_copy_complete(self):
        """Called when copy process finishes."""
        self.is_copying = False
        if self.cancelled:
            self.copy_process = None
            self.progress_var.set("Copy cancelled.")
            self.copy_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            return
        if self.copy_process:
            self.copy_process.wait()
            exit_code = self.copy_process.returncode
            self.copy_process = None

            if self.total_files is not None:
                self.progress_var.set(
                    f"{self.total_files} of {self.total_files} files processed - Complete!"
                )
            else:
                self.progress_var.set(f"{self.files_copied} files processed - Complete!")

            if exit_code >= 8:
                self.status_var.set(f"Copy completed with errors (exit code: {exit_code})")
                messagebox.showwarning(
                    "Copy Completed with Errors",
                    f"Copy finished with exit code {exit_code}.\n\n"
                    f"Log file: {self.log_file}\n\n"
                    "Some files may not have been copied.",
                )
            else:
                self.status_var.set("Copy completed successfully!")
                messagebox.showinfo(
                    "Copy Completed",
                    f"File copy completed successfully!\n\n"
                    f"{self.total_files or self.files_copied} files processed.\n\n"
                    f"Full log saved to:\n{self.log_file}",
                )

        self.copy_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def stop_copy(self):
        """Stop the copy process."""
        self.is_copying = False
        self.cancelled = True
        if self.copy_process:
            self.copy_process.terminate()
        self.status_var.set("Copy cancelled.")
        self.progress_var.set("Copy cancelled.")
        self.copy_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        if self.log_file and os.path.exists(self.log_file):
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write("\n[Cancelled by user]\n")
            except OSError:
                pass
        messagebox.showinfo("Cancelled", "Copy operation was cancelled.")

    def run(self):
        self.root.mainloop()


def main():
    try:
        app = TurboCopyGUI()
        app.run()
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("TurboCopy Error", f"Failed to start:\n\n{str(e)}\n\nSee Console for details.")
        except Exception:
            print("TurboCopy failed to start:", file=sys.stderr)
            print(err, file=sys.stderr)
        raise

if __name__ == "__main__":
    main()
