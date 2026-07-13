import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import yt_dlp
from PIL import Image
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("dark")


app = ctk.CTk()
app.iconbitmap(resource_path("assets/icon.ico"))
app.title("Flow Fetch")
app.geometry("700x650")
app.resizable(False, False)

logo = ctk.CTkImage(
    light_image=Image.open(resource_path("assets/logo.png")),
    dark_image=Image.open(resource_path("assets/logo.png")),
    size=(140, 140)
)


folder = ""


def choose_folder():
    global folder
    folder = filedialog.askdirectory()
    if folder:
        folder_label.configure(text=folder)


def show_error(message):
    status.configure(text=f"🔴 {message}", text_color="#F44336")
    messagebox.showerror("Flow Fetch", message)


def show_info(message):
    status.configure(text=message, text_color="#2196F3")


# ================= Title =================
title_frame = ctk.CTkFrame(app, fg_color="transparent")
title_frame.pack(pady=15)

flow_label = ctk.CTkLabel(
    title_frame,
    text="FLOW ",
    font=("Segoe UI",30,"bold"),
    text_color="#FFFFFF"
)
flow_label.pack(side="left")

fetch_label = ctk.CTkLabel(
    title_frame,
    text="FETCH",
    font=("Segoe UI",30,"bold"),
    text_color="#D62828"  # أحمر
)
fetch_label.pack(side="left")


subtitle = ctk.CTkLabel(
    app,
    text="Download YouTube Playlists & Videos",
    font=("Segoe UI",13),
    text_color="#AAAAAA"
)

subtitle.pack(pady=(0,20))


url_entry = ctk.CTkEntry(
    app,
    width=550,
    height=42,
    corner_radius=10,
    placeholder_text="Paste YouTube Playlist or Video URL..."
)
url_entry.pack(pady=15)


# ================= Right Click Paste Menu =================

import tkinter as tk


def show_context_menu(event):

    menu = tk.Menu(
        app,
        tearoff=0
    )

    menu.add_command(
        label="Paste",
        command=lambda: url_entry.insert("insert", app.clipboard_get())
    )

    menu.add_command(
        label="Copy",
        command=lambda: app.clipboard_append(url_entry.get())
    )

    menu.add_command(
        label="Cut",
        command=lambda: (
            app.clipboard_clear(),
            app.clipboard_append(url_entry.get()),
            url_entry.delete(0, "end")
        )
    )

    menu.post(
        event.x_root,
        event.y_root
    )


def paste_from_clipboard(event=None):
    try:
        url_entry.insert("insert", app.clipboard_get())
    except tk.TclError:
        pass
    return "break"

url_entry.bind(
    "<Button-3>",
    show_context_menu
)
url_entry.bind(
    "<Control-v>",
    paste_from_clipboard
)
url_entry.bind(
    "<Control-V>",
    paste_from_clipboard
)


quality_menu = ctk.CTkOptionMenu(
    app,
    width=220,
    height=40,
    corner_radius=8,
    values=["480p","720p","1080p", "Best Quality"],
)

quality_menu.set("Select Quality")
quality_menu.pack(pady=10)


folder_btn = ctk.CTkButton(
    app,
    text="Browse Folder",
    command=choose_folder,
    fg_color="#D62828",
    hover_color="#B71C1C",
    corner_radius=8,
    height=40,
)

folder_btn.pack(pady=10)


folder_label = ctk.CTkLabel(
    app,
    text="No folder selected"
)

folder_label.pack()


start_btn = ctk.CTkButton(
    app,
    text="Start Download",
    command=lambda: download(),
    fg_color="#D62828",
    hover_color="#B71C1C",
    corner_radius=8,
    height=45,
    font=("Segoe UI",15,"bold"),
)

start_btn.pack(pady=20)

# ================= Preview Feature =================
import webbrowser

def preview_video():
    url = url_entry.get().strip()
    if not url:
        show_error("Please paste a YouTube URL first.")
        return

    options = {"quiet": True, "skip_download": True}
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception:
        show_error("Unable to preview video. Please check the link and try again.")
        return

    preview_win = ctk.CTkToplevel(app)
    preview_win.title("Video Preview")
    preview_win.geometry("500x320")

    # Title
    title_label = ctk.CTkLabel(preview_win, text=f"Title: {info.get('title', 'Unknown')}")
    title_label.pack(pady=10)

    # Duration
    duration_label = ctk.CTkLabel(preview_win, text=f"Duration: {info.get('duration', 0)} seconds")
    duration_label.pack(pady=10)

    # Chosen quality only
    chosen_quality = quality_menu.get()
    available_heights = [f.get('height') for f in info.get("formats", []) if f.get('height')]

    if chosen_quality != "Best Quality":
        try:
            chosen_height = int(chosen_quality.replace("p",""))
            if chosen_height not in available_heights:
                chosen_label = ctk.CTkLabel(
                    preview_win,
                    text=f"⚠️ {chosen_quality} not available, highest available will be downloaded ({max(available_heights)}p)"
                )
            else:
                chosen_label = ctk.CTkLabel(preview_win, text=f"Chosen Quality: {chosen_quality}")
        except:
            chosen_label = ctk.CTkLabel(preview_win, text=f"Chosen Quality: {chosen_quality}")
    else:
        chosen_label = ctk.CTkLabel(preview_win, text="Chosen Quality: Best Quality")
    chosen_label.pack(pady=10)

    # Play online button
    youtube_url = info.get('webpage_url') or f"https://www.youtube.com/watch?v={info.get('id')}"
    play_btn = ctk.CTkButton(preview_win, text="Play Online", command=lambda: webbrowser.open(youtube_url))
    play_btn.pack(pady=20)

# Add preview button in the main UI
preview_btn = ctk.CTkButton(
    app,
    text="Preview Video",
    command=preview_video,
    fg_color="#FFFFFF",
    text_color="#2196F3",
    hover_color="#E0E0E0",
    corner_radius=8,
    height=40
)
preview_btn.pack(pady=10)

# ================= Progress Bar =================
progress_bar = ctk.CTkProgressBar(app, width=500)
progress_bar.set(0)  # يبدأ من صفر
progress_bar.pack(pady=10)

progress_label = ctk.CTkLabel(app, text="0%")
progress_label.pack()

# ================= Status Label =================
status = ctk.CTkLabel(
    app,
    text="🔵 Ready",   # أزرق في البداية
    font=("Segoe UI", 16, "bold"),
    text_color="#2196F3"  # أزرق
)
status.pack(pady=15)

def progress_hook(d):
    if d['status'] == 'downloading':
        status.configure(text="🟡 Downloading...", text_color="#FFC107")  # أصفر
        total = d.get('total_bytes', 0)
        downloaded = d.get('downloaded_bytes', 0)
        if total > 0:
            progress = downloaded / total
            progress_bar.set(downloaded / total)
            percent = int((downloaded / total) * 100)
            progress_label.configure(text=f"{percent}%")
    elif d['status'] == 'finished':
        status.configure(text="🟢 Finished", text_color="#4CAF50")  # أخضر
        progress_bar.set(1.0)
        progress_label.configure(text="100%")
    elif d['status'] == 'error':
        status.configure(text="🔴 Error", text_color="#F44336")  # أحمر

def download():
    url = url_entry.get().strip()
    quality = quality_menu.get()

    if not url:
        show_error("Please paste a YouTube URL first.")
        return

    if not folder:
        show_error("Please select a download folder.")
        return

    if quality == "Select Quality":
        show_error("Please choose a download quality.")
        return

    def worker():
        if quality == "Best Quality":
            options = {
                "format": "bestvideo*+bestaudio/best",
                "merge_output_format": "mp4",
                "outtmpl": f"{folder}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s",
                "noplaylist": False,
                "ignoreerrors": True,
                "progress_hooks": [progress_hook]
            }
        else:
            try:
                height = int(quality.replace("p", ""))
            except ValueError:
                height = None

            options = {
                "format": f"bestvideo[height<={height}]+bestaudio/best" if height else "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "outtmpl": f"{folder}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s",
                "noplaylist": False,
                "ignoreerrors": True,
                "progress_hooks": [progress_hook]
            }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
        except Exception:
            app.after(0, lambda: show_error("Download failed. Please check the URL and try again."))

    status.configure(text="🟡 Downloading...", text_color="#FFC107")
    progress_bar.set(0)   # إعادة التهيئة
    progress_label.configure(text="0%")
    threading.Thread(target=worker, daemon=True).start()


app.mainloop()
