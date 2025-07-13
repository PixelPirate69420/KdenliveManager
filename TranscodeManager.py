#!/usr/bin/env python3
import os
import subprocess
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil

def ffprobe_json(filepath):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', '-show_format', filepath]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        return {}

def scan_folder_for_transcodes(folder):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    matrix = []
    delete_list = []
    for file in files:
        info = ffprobe_json(file)
        matrix.append((file, info))
        if "fps" in file.lower() and "Lavc" in json.dumps(info):
            delete_list.append(file)
    return matrix, delete_list

def delete_transcodes():
    folder = filedialog.askdirectory(title="Select Folder to Delete Transcodes From")
    if not folder:
        return
    _, delete_list = scan_folder_for_transcodes(folder)
    if not delete_list:
        messagebox.showinfo("Info", "No matching transcodes found.")
        return

    file_preview = "\n".join(os.path.basename(f) for f in delete_list[:10])
    if len(delete_list) > 10:
        file_preview += f"\n...and {len(delete_list) - 10} more files"

    if messagebox.askyesno("Confirm Deletion", f"Delete {len(delete_list)} files?\n\n{file_preview}"):
        for f in delete_list:
            os.remove(f)
        messagebox.showinfo("Done", f"Deleted {len(delete_list)} files.")

def copy_or_move_transcodes(move=False):
    src_folder = filedialog.askdirectory(title="Select Source Folder")
    if not src_folder:
        return
    dest_folder = filedialog.askdirectory(title="Select Destination Folder")
    if not dest_folder:
        return

    _, files = scan_folder_for_transcodes(src_folder)
    if not files:
        messagebox.showinfo("Info", "No matching transcodes found.")
        return

    for f in files:
        try:
            if move:
                shutil.move(f, os.path.join(dest_folder, os.path.basename(f)))
            else:
                shutil.copy(f, os.path.join(dest_folder, os.path.basename(f)))
        except Exception as e:
            print(f"Error: {e}")

    action = "Moved" if move else "Copied"
    messagebox.showinfo("Done", f"{action} {len(files)} files.")

def find_transcodes():
    folder = filedialog.askdirectory(title="Select Folder to Analyze")
    if not folder:
        return
    _, files = scan_folder_for_transcodes(folder)
    total_size = sum(os.path.getsize(f) for f in files)
    messagebox.showinfo(
        "Scan Results",
        f"Found {len(files)} transcodes\nTotal size: {total_size / 1024 / 1024:.2f} MB"
    )

# === GUI Setup ===
root = tk.Tk()
root.title("Transcode Manager")
root.geometry("800x400")

font_cfg = ("Arial", 16)
pad = {"padx": 20, "pady": 15}

frame = tk.Frame(root)
frame.pack(expand=True)

tk.Button(frame, text="1. Delete Transcodes", font=font_cfg, width=30, height=2,
          command=delete_transcodes).pack(**pad)
tk.Button(frame, text="2. Copy Transcodes", font=font_cfg, width=30, height=2,
          command=lambda: copy_or_move_transcodes(move=False)).pack(**pad)
tk.Button(frame, text="3. Move Transcodes", font=font_cfg, width=30, height=2,
          command=lambda: copy_or_move_transcodes(move=True)).pack(**pad)
tk.Button(frame, text="4. Find Transcodes", font=font_cfg, width=30, height=2,
          command=find_transcodes).pack(**pad)

root.mainloop()
