"""Tkinter desktop interface for Prism Extractor."""
from __future__ import annotations
import json
import queue
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from .save_file import save_channel_results
from .videos import extract_channel, normalize_channel_url

ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = ROOT / "settings.json"

class PrismApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prism Extractor")
        self.root.geometry("1120x760")
        self.root.minsize(820, 560)
        self.events = queue.Queue()
        self.executor = None
        self.cards = {}
        self.active = 0
        self._build()
        self.root.after(100, self._drain_events)

    def _build(self):
        style = ttk.Style()
        try: style.theme_use("clam")
        except tk.TclError: pass
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="PRISM EXTRACTOR", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Monitor every channel worker independently.", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 12))
        controls = ttk.LabelFrame(outer, text="Run settings", padding=10)
        controls.pack(fill="x", pady=(0, 10))
        ttk.Label(controls, text="YouTube channels (one URL or @handle per line)").grid(row=0, column=0, sticky="w")
        self.channels = tk.Text(controls, height=4, wrap="word", font=("Consolas", 10))
        self.channels.grid(row=1, column=0, sticky="nsew", padx=(0, 12), pady=5)
        side = ttk.Frame(controls)
        side.grid(row=1, column=1, sticky="ns")
        ttk.Label(side, text="Concurrent workers").pack(anchor="w")
        self.worker_count = tk.IntVar(value=3)
        ttk.Spinbox(side, from_=1, to=16, width=7, textvariable=self.worker_count).pack(anchor="w", pady=(3, 12))
        self.start_button = ttk.Button(side, text="Start extraction", command=self.start)
        self.start_button.pack(fill="x")
        self.summary = tk.StringVar(value="Ready")
        ttk.Label(side, textvariable=self.summary, wraplength=180).pack(anchor="w", pady=(12, 0))
        controls.columnconfigure(0, weight=1)
        ttk.Label(outer, text="WORKERS", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 6))
        holder = ttk.Frame(outer)
        holder.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(holder, highlightthickness=0)
        scrollbar = ttk.Scrollbar(holder, orient="vertical", command=self.canvas.yview)
        self.worker_frame = ttk.Frame(self.canvas)
        self.worker_frame.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.window_id = self.canvas.create_window((0, 0), window=self.worker_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.window_id, width=e.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _add_card(self, index, channel):
        card = ttk.LabelFrame(self.worker_frame, text=f"Worker {index}: {channel}", padding=9)
        card.pack(fill="x", pady=5, padx=2)
        top = ttk.Frame(card); top.pack(fill="x")
        status = tk.StringVar(value="Queued")
        ttk.Label(top, textvariable=status, font=("Segoe UI", 9, "bold")).pack(side="left")
        progress = ttk.Progressbar(top, mode="determinate", maximum=100)
        progress.pack(side="right", fill="x", expand=True, padx=(12, 0))
        log = tk.Text(card, height=7, wrap="word", state="disabled", font=("Consolas", 9),
                      background="#101820", foreground="#d7e2ea", insertbackground="#ffffff")
        log.pack(fill="x", pady=(7, 0))
        self.cards[channel] = {"status": status, "progress": progress, "log": log}

    def _log(self, channel, message):
        card = self.cards.get(channel)
        if not card: return
        widget = card["log"]
        widget.configure(state="normal")
        widget.insert("end", message.rstrip() + "\n")
        widget.see("end")
        widget.configure(state="disabled")

    def start(self):
        if self.active: return
        raw = self.channels.get("1.0", "end").splitlines()
        channels = list(dict.fromkeys(line.strip() for line in raw if line.strip()))
        if not channels:
            messagebox.showinfo("No channels", "Enter at least one YouTube channel URL or @handle.")
            return
        try:
            normalized = [normalize_channel_url(value) for value in channels]
            workers = int(self.worker_count.get())
            if workers < 1: raise ValueError("Worker count must be positive.")
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Invalid input", str(exc)); return
        for child in self.worker_frame.winfo_children(): child.destroy()
        self.cards.clear()
        for index, channel in enumerate(normalized, start=1): self._add_card(index, channel)
        self.active = len(normalized)
        self.start_button.configure(state="disabled")
        self.summary.set(f"Running {len(normalized)} channel(s), {min(workers, len(normalized))} concurrent worker(s)")
        with SETTINGS_PATH.open(encoding="utf-8") as stream: settings = json.load(stream)
        settings.setdefault("concurrency", {})
        settings["concurrency"].setdefault("channels", 3)
        self.executor = ThreadPoolExecutor(max_workers=min(workers, len(normalized)), thread_name_prefix="prism-gui")
        for channel in normalized: self.executor.submit(self._run_channel, channel, settings)

    def _run_channel(self, channel, settings):
        def report(message, current=None, total=None, status=None):
            self.events.put(("update", channel, message, current, total, status))
        try:
            report("Starting channel discovery…", status="Discovering")
            result = extract_channel(channel, settings, progress_callback=report)
            report("Saving results…", status="Saving")
            output = save_channel_results(result, settings)
            report(f"Saved {len(result['videos'])} video record(s) to {output}", status="Completed")
            if result.get("failures"): report(f"{len(result['failures'])} video(s) could not be processed.")
            self.events.put(("finished", channel, True))
        except Exception as exc:
            report(f"ERROR: {exc}", status="Failed")
            self.events.put(("finished", channel, False))

    def _drain_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "update":
                    _, channel, message, current, total, status = event
                    self._log(channel, message)
                    card = self.cards.get(channel)
                    if card:
                        if status: card["status"].set(status)
                        if total:
                            card["progress"]["maximum"] = total
                            card["progress"]["value"] = current or 0
                else:
                    self.active -= 1
                    if self.active <= 0:
                        self.start_button.configure(state="normal")
                        done = sum(c["status"].get() == "Completed" for c in self.cards.values())
                        failed = sum(c["status"].get() == "Failed" for c in self.cards.values())
                        self.summary.set(f"Finished — {done} completed, {failed} failed")
                        if self.executor:
                            self.executor.shutdown(wait=False); self.executor = None
        except queue.Empty: pass
        self.root.after(100, self._drain_events)

    def close(self):
        if self.executor: self.executor.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()

def main():
    root = tk.Tk()
    PrismApp(root)
    root.mainloop()

if __name__ == "__main__": main()
