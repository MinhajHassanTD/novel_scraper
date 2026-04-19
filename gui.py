import tkinter as tk
from tkinter import ttk, filedialog
import threading
import os
import sys
import subprocess
import cloudscraper
from fetch_webpage import fetch, fetch_metadata

C = {
    "bg":             "#1C1C1C",
    "surface":        "#252525",
    "border":         "#3A3A3A",
    "accent":         "#C8975A",
    "accent_hover":   "#DBA86A",
    "accent_dim":     "#7A5A34",
    "text_primary":   "#E8DCC8",
    "text_secondary": "#9A8E7C",
    "text_disabled":  "#5A5248",
    "log_bg":         "#141414",
    "log_fg":         "#C0B49A",
    "success":        "#6A9E6A",
    "error":          "#C06060",
    "entry_bg":       "#2A2A2A",
    "progress_trough":"#2E2E2E",
}

FONT       = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_HEAD  = ("Segoe UI", 13, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_MONO  = ("Consolas", 9)


class NovelScraperGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.withdraw()  # hide until fully styled to prevent white flash
        root.title("Novel Scraper")
        root.resizable(False, False)
        root.configure(bg=C["bg"])

        self._cancel_event = threading.Event()
        self._cover_bytes: bytes | None = None
        self._chapter_times: list[float] = []

        self._setup_style()
        self._build_ui()
        self._center_window()
        root.deiconify()

    def _center_window(self) -> None:
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    # ── Style ─────────────────────────────────────────────────────────────

    def _setup_style(self) -> None:
        s = ttk.Style(self.root)
        s.theme_use("clam")

        s.configure("TFrame", background=C["bg"])
        s.configure("Surface.TFrame", background=C["surface"])

        s.configure("TLabel", background=C["bg"], foreground=C["text_primary"], font=FONT)
        s.configure("Header.TLabel", background=C["bg"], foreground=C["accent"], font=FONT_HEAD)
        s.configure("Surface.TLabel", background=C["surface"], foreground=C["text_primary"], font=FONT)
        s.configure("Status.TLabel", background=C["bg"], foreground=C["text_secondary"], font=FONT_SMALL)
        s.configure("ETA.TLabel", background=C["bg"], foreground=C["text_secondary"], font=FONT_SMALL)

        s.configure("TSeparator", background=C["border"])

        s.configure("TEntry",
                    fieldbackground=C["entry_bg"], foreground=C["text_primary"],
                    insertcolor=C["accent"], bordercolor=C["border"],
                    lightcolor=C["border"], darkcolor=C["border"], padding=(6, 4))
        s.map("TEntry",
              bordercolor=[("focus", C["accent"])],
              lightcolor=[("focus", C["accent"])])

        s.configure("Accent.TButton",
                    background=C["accent"], foreground=C["bg"],
                    font=FONT_BOLD, borderwidth=0, relief="flat", padding=(0, 10))
        s.map("Accent.TButton",
              background=[("active", C["accent_hover"]), ("disabled", C["accent_dim"])],
              foreground=[("disabled", C["text_disabled"])])

        s.configure("Small.TButton",
                    background=C["surface"], foreground=C["text_primary"],
                    font=FONT_SMALL, bordercolor=C["border"],
                    lightcolor=C["border"], darkcolor=C["border"],
                    relief="flat", padding=(6, 4))
        s.map("Small.TButton",
              background=[("active", C["border"]), ("disabled", C["surface"])],
              foreground=[("disabled", C["text_disabled"])])

        s.configure("Warm.Horizontal.TProgressbar",
                    troughcolor=C["progress_trough"], background=C["accent"],
                    bordercolor=C["progress_trough"], lightcolor=C["accent"],
                    darkcolor=C["accent"], thickness=8)

        s.configure("TScrollbar",
                    background=C["border"], troughcolor=C["log_bg"],
                    bordercolor=C["log_bg"], arrowcolor=C["text_secondary"],
                    relief="flat", arrowsize=12)
        s.map("TScrollbar", background=[("active", C["text_disabled"])])

        s.configure("TCheckbutton",
                    background=C["surface"], foreground=C["text_primary"], font=FONT)
        s.map("TCheckbutton",
              background=[("active", C["surface"])],
              indicatorcolor=[("selected", C["accent"]), ("active", C["accent_hover"])])

        s.configure("TLabelframe",
                    background=C["surface"], bordercolor=C["border"],
                    relief="groove", borderwidth=1)
        s.configure("TLabelframe.Label",
                    background=C["surface"], foreground=C["accent"], font=FONT_SMALL)

    # ── Layout ────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=(16, 12))
        outer.grid(sticky="nsew")

        # Header
        ttk.Label(outer, text="Novel Scraper", style="Header.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Separator(outer, orient="horizontal").grid(
            row=1, column=0, sticky="ew", pady=(0, 10))

        # Fields card
        card = ttk.Frame(outer, style="Surface.TFrame", padding=(12, 10))
        card.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        card.columnconfigure(1, weight=1)

        def label(parent: ttk.Frame, text: str, row: int) -> None:
            ttk.Label(parent, text=text, style="Surface.TLabel").grid(
                row=row, column=0, sticky="e", padx=(0, 8), pady=4)

        # Title
        self.title_var = tk.StringVar(value="Shadow Slave")
        label(card, "Novel Title:", 0)
        ttk.Entry(card, textvariable=self.title_var).grid(
            row=0, column=1, columnspan=3, sticky="ew", pady=4)

        # Author
        self.author_var = tk.StringVar(value="Guiltythree")
        label(card, "Author:", 1)
        ttk.Entry(card, textvariable=self.author_var).grid(
            row=1, column=1, columnspan=3, sticky="ew", pady=4)

        # URL row: entry + Paste + Auto-fill
        self.url_var = tk.StringVar(
            value="https://novelbin.com/b/shadow-slave/chapter-1-nightmare-begins")
        label(card, "Start URL:", 2)
        ttk.Entry(card, textvariable=self.url_var).grid(
            row=2, column=1, sticky="ew", pady=4, padx=(0, 4))
        ttk.Button(card, text="Paste", style="Small.TButton",
                   command=self._paste_url).grid(row=2, column=2, pady=4, padx=(0, 4))
        self.autofill_btn = ttk.Button(card, text="Auto-fill", style="Small.TButton",
                                       command=self._auto_fill)
        self.autofill_btn.grid(row=2, column=3, pady=4)

        # Save row
        self.save_var = tk.StringVar(value=os.path.expanduser("~\\Desktop"))
        label(card, "Save to:", 3)
        ttk.Entry(card, textvariable=self.save_var).grid(
            row=3, column=1, columnspan=2, sticky="ew", pady=4, padx=(0, 4))
        ttk.Button(card, text="Browse", style="Small.TButton",
                   command=self._browse).grid(row=3, column=3, pady=4)

        # Options LabelFrame
        opts = ttk.LabelFrame(card, text="Options", padding=(10, 6))
        opts.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(8, 2))
        opts.columnconfigure((1, 3), weight=1)

        self.start_var = tk.StringVar(value="1")
        self.end_var   = tk.StringVar(value="0")
        self.delay_var = tk.StringVar(value="1.0")
        self.open_var  = tk.BooleanVar(value=True)
        self.cover_var = tk.BooleanVar(value=True)

        ttk.Label(opts, text="Start Ch:", style="Surface.TLabel").grid(
            row=0, column=0, sticky="e", padx=(0, 4), pady=3)
        ttk.Entry(opts, textvariable=self.start_var, width=6).grid(
            row=0, column=1, sticky="w", pady=3)

        ttk.Label(opts, text="End Ch (0=all):", style="Surface.TLabel").grid(
            row=0, column=2, sticky="e", padx=(12, 4), pady=3)
        ttk.Entry(opts, textvariable=self.end_var, width=6).grid(
            row=0, column=3, sticky="w", pady=3)

        ttk.Label(opts, text="Delay (s):", style="Surface.TLabel").grid(
            row=1, column=0, sticky="e", padx=(0, 4), pady=3)
        ttk.Entry(opts, textvariable=self.delay_var, width=6).grid(
            row=1, column=1, sticky="w", pady=3)

        ttk.Checkbutton(opts, text="Open EPUB when done", variable=self.open_var).grid(
            row=1, column=2, sticky="w", padx=(12, 0), pady=3)
        ttk.Checkbutton(opts, text="Fetch cover art", variable=self.cover_var).grid(
            row=1, column=3, sticky="w", pady=3)

        # Start button
        self.start_btn = ttk.Button(outer, text="Start Scraping",
                                    style="Accent.TButton", command=self._start)
        self.start_btn.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        # Log pane (manual Text + Scrollbar for full styling control)
        log_frame = ttk.Frame(outer)
        log_frame.grid(row=4, column=0, sticky="ew", pady=(0, 6))
        log_frame.columnconfigure(0, weight=1)

        self.log = tk.Text(
            log_frame, height=14, width=72,
            bg=C["log_bg"], fg=C["log_fg"], insertbackground=C["accent"],
            selectbackground=C["accent_dim"], selectforeground=C["text_primary"],
            font=FONT_MONO, relief="flat", borderwidth=0, padx=8, pady=6,
            state="disabled", wrap="word",
        )
        self.log.tag_configure("success", foreground=C["success"])
        self.log.tag_configure("error",   foreground=C["error"])
        sb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        self.log.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

        # ETA label
        self.eta_var = tk.StringVar(value="")
        self.eta_label = ttk.Label(outer, textvariable=self.eta_var, style="ETA.TLabel")
        self.eta_label.grid(row=5, column=0, sticky="w", pady=(0, 2))

        # Progress bar
        self.progress = ttk.Progressbar(
            outer, style="Warm.Horizontal.TProgressbar",
            mode="indeterminate", length=600)
        self.progress.grid(row=6, column=0, sticky="ew", pady=(0, 6))

        # Bottom row: status (left) + Cancel (right)
        bottom = ttk.Frame(outer)
        bottom.grid(row=7, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(bottom, text="Ready", style="Status.TLabel")
        self.status_label.grid(row=0, column=0, sticky="w")

        self.cancel_btn = ttk.Button(bottom, text="Cancel", style="Small.TButton",
                                     command=self._cancel, state="disabled")
        self.cancel_btn.grid(row=0, column=1, sticky="e")

    # ── Actions ───────────────────────────────────────────────────────────

    def _paste_url(self) -> None:
        try:
            self.url_var.set(self.root.clipboard_get())
        except tk.TclError:
            pass

    def _browse(self) -> None:
        path = filedialog.askdirectory(title="Select save directory")
        if path:
            self.save_var.set(path)

    def _auto_fill(self) -> None:
        url = self.url_var.get().strip()
        if not url:
            return
        self.autofill_btn.configure(state="disabled", text="Filling…")
        self._append_log("Auto-filling metadata…")
        threading.Thread(target=self._run_autofill, args=(url,), daemon=True).start()

    def _run_autofill(self, url: str) -> None:
        try:
            scraper = cloudscraper.create_scraper()  # pyright: ignore[reportUnknownMemberType]
            title, author, cover = fetch_metadata(url, scraper)
            def apply() -> None:
                if title:
                    self.title_var.set(title)
                if author:
                    self.author_var.set(author)
                self._cover_bytes = cover
                filled = []
                if title: filled.append(f"title: {title}")
                if author: filled.append(f"author: {author}")
                cover_msg = " | cover: found" if cover else " | cover: not found"
                self._append_log("  Got " + ", ".join(filled) + cover_msg if filled else "  Nothing detected")
                self.autofill_btn.configure(state="normal", text="Auto-fill")
            self.root.after(0, apply)
        except Exception as e:
            self.root.after(0, self._append_log, f"  Auto-fill error: {e}")
            self.root.after(0, self.autofill_btn.configure, {"state": "normal", "text": "Auto-fill"})

    def _cancel(self) -> None:
        self._cancel_event.set()
        self.cancel_btn.configure(state="disabled")
        self.status_label.configure(foreground=C["text_secondary"], text="Cancelling…")

    def _start(self) -> None:
        self._cancel_event.clear()
        self._chapter_times = []
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.eta_var.set("")
        self.status_label.configure(foreground=C["text_secondary"], text="Fetching…")
        self.start_btn.configure(state="disabled", text="Scraping…")
        self.cancel_btn.configure(state="normal")
        self.progress.start(12)
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self) -> None:
        try:
            end_ch  = int(self.end_var.get() or 0)
            start_ch = int(self.start_var.get() or 1)
            output = fetch(
                start_url=self.url_var.get().strip(),
                title=self.title_var.get().strip(),
                author=self.author_var.get().strip(),
                start_chapter=start_ch,
                end_chapter=end_ch,
                delay=float(self.delay_var.get() or 1.0),
                save_dir=self.save_var.get().strip(),
                cover=self._cover_bytes if self.cover_var.get() else None,
                cancel_event=self._cancel_event,
                progress_callback=self._log,
                on_chapter_done=self._on_chapter_done,
            )
            self._output_path = output
            self.root.after(0, self._done, f"Done — {os.path.basename(output)}", True)
        except Exception as e:
            self.root.after(0, self._done, f"Error: {e}", False)

    def _done(self, msg: str, success: bool = True) -> None:
        self.progress.stop()
        self.start_btn.configure(state="normal", text="Start Scraping")
        self.cancel_btn.configure(state="disabled")
        color = C["success"] if success else C["error"]
        self.status_label.configure(foreground=color, text=msg)
        if success and self.open_var.get() and hasattr(self, "_output_path"):
            try:
                if sys.platform == "win32":
                    os.startfile(self._output_path)
                else:
                    subprocess.Popen(["xdg-open", self._output_path])
            except Exception:
                pass

    # ── Logging & ETA ─────────────────────────────────────────────────────

    def _log(self, msg: str) -> None:
        self.root.after(0, self._append_log, msg)

    def _append_log(self, msg: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _on_chapter_done(self, ch_idx: int, elapsed: float) -> None:
        self._chapter_times.append(elapsed)
        avg = sum(self._chapter_times) / len(self._chapter_times)
        end_ch = int(self.end_var.get() or 0)
        start_ch = int(self.start_var.get() or 1)
        if end_ch > 0:
            total = end_ch - start_ch + 1
            remaining = max(0, total - ch_idx)
            eta_secs = int(avg * remaining)
            if eta_secs >= 60:
                eta_str = f"{eta_secs // 60}m {eta_secs % 60}s"
            else:
                eta_str = f"{eta_secs}s"
            text = f"Chapter: {ch_idx}/{total}  |  Avg: {avg:.1f}s/ch  |  ETA: {eta_str}"
        else:
            text = f"Chapter: {ch_idx} fetched  |  Avg: {avg:.1f}s/ch"
        self.root.after(0, self.eta_var.set, text)


if __name__ == "__main__":
    root = tk.Tk()
    NovelScraperGUI(root)
    root.mainloop()
