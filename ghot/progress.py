import os
import sys
import threading
import time
from contextlib import contextmanager

from colorama import Fore, Style


SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def _supports_tty(stream):
    try:
        return stream.isatty()
    except Exception:
        return False


class ProgressRenderer:
    """Docker-build style live progress.

    Completed rows scroll above; active rows redraw in place with a spinner.
    Falls back to plain line-by-line output when the stream is not a TTY.
    """

    def __init__(self, total, enabled=True, stream=None, refresh_interval=0.1, max_active_rows=12):
        self.total = total
        self.stream = stream or sys.stdout
        self.enabled = bool(enabled) and _supports_tty(self.stream)
        self.refresh_interval = refresh_interval
        self.max_active_rows = max_active_rows

        self._completed = 0
        self._started_at = None
        self._active = {}  # uid -> {"msg": str, "started": float}
        self._active_order = []  # for stable display order
        self._lock = threading.RLock()
        self._prompt_lock = threading.Lock()
        self._paused = threading.Event()
        self._stop = threading.Event()
        self._thread = None
        self._spin_idx = 0
        self._lines_drawn = 0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()

    def start(self):
        if not self.enabled:
            return
        self._started_at = time.time()
        self._hide_cursor()
        self._thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if not self.enabled:
            return
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        with self._lock:
            self._erase()
            self._print_summary()
            self._show_cursor()
            self.stream.flush()

    def begin_task(self, uid, message="queued"):
        with self._lock:
            if uid not in self._active:
                self._active_order.append(uid)
            self._active[uid] = {"msg": message, "started": time.time()}

    def update_task(self, uid, message):
        with self._lock:
            if uid in self._active:
                self._active[uid]["msg"] = message

    def complete_task(self, uid, line):
        with self._lock:
            self._completed += 1
            if uid in self._active:
                self._active.pop(uid, None)
                try:
                    self._active_order.remove(uid)
                except ValueError:
                    pass
            if self.enabled:
                self._erase()
                self.stream.write(line + "\n")
                self._draw()
                self.stream.flush()
            else:
                self.stream.write(line + "\n")
                self.stream.flush()

    def print_line(self, line):
        """Print a static line above the active section."""
        with self._lock:
            if self.enabled:
                self._erase()
                self.stream.write(line + "\n")
                self._draw()
                self.stream.flush()
            else:
                self.stream.write(line + "\n")
                self.stream.flush()

    @contextmanager
    def prompt(self):
        """Pause rendering for synchronous user input. Serialized across threads."""
        with self._prompt_lock:
            if not self.enabled:
                yield
                return
            self._paused.set()
            with self._lock:
                self._erase()
                self._show_cursor()
                self.stream.flush()
            try:
                yield
            finally:
                with self._lock:
                    self._hide_cursor()
                self._paused.clear()

    def _refresh_loop(self):
        while not self._stop.wait(self.refresh_interval):
            if self._paused.is_set():
                continue
            with self._lock:
                self._spin_idx = (self._spin_idx + 1) % len(SPINNER_FRAMES)
                self._erase()
                self._draw()
                self.stream.flush()

    def _erase(self):
        if self._lines_drawn <= 0:
            return
        for _ in range(self._lines_drawn):
            self.stream.write("\033[F\033[2K")
        self._lines_drawn = 0

    def _draw(self):
        spin = SPINNER_FRAMES[self._spin_idx]
        elapsed = time.time() - (self._started_at or time.time())
        total = self.total
        done = self._completed
        running = len(self._active)
        bar = self._bar(done, total)
        header = (
            f"{Style.BRIGHT}{Fore.CYAN}{spin}{Style.RESET_ALL} "
            f"{bar} "
            f"{Style.BRIGHT}{done}/{total}{Style.RESET_ALL} "
            f"{Style.DIM}({running} running, {elapsed:5.1f}s){Style.RESET_ALL}"
        )
        self.stream.write(header + "\n")
        lines = 1
        shown = self._active_order[: self.max_active_rows]
        for uid in shown:
            info = self._active.get(uid)
            if not info:
                continue
            task_elapsed = time.time() - info["started"]
            line = (
                f"  {Fore.CYAN}{spin}{Style.RESET_ALL} "
                f"{Style.BRIGHT}{Fore.GREEN}{uid}{Style.RESET_ALL} "
                f"{Style.DIM}{info['msg']} ({task_elapsed:4.1f}s){Style.RESET_ALL}"
            )
            self.stream.write(line + "\n")
            lines += 1
        overflow = len(self._active_order) - len(shown)
        if overflow > 0:
            self.stream.write(f"  {Style.DIM}... and {overflow} more{Style.RESET_ALL}\n")
            lines += 1
        self._lines_drawn = lines

    def _bar(self, done, total, width=24):
        if total <= 0:
            return "[" + " " * width + "]"
        filled = int(width * done / total)
        return "[" + Fore.GREEN + "█" * filled + Style.RESET_ALL + " " * (width - filled) + "]"

    def _print_summary(self):
        if not self._started_at:
            return
        elapsed = time.time() - self._started_at
        self.stream.write(
            f"{Style.BRIGHT}Done{Style.RESET_ALL} "
            f"{self._completed}/{self.total} "
            f"{Style.DIM}in {elapsed:.1f}s{Style.RESET_ALL}\n"
        )

    def _hide_cursor(self):
        if self.enabled:
            self.stream.write("\033[?25l")
            self.stream.flush()

    def _show_cursor(self):
        if self.enabled:
            self.stream.write("\033[?25h")
            self.stream.flush()


def detect_enabled(no_progress=False, stream=None):
    stream = stream or sys.stdout
    if no_progress:
        return False
    if os.environ.get("NO_COLOR") or os.environ.get("CI"):
        return False
    return _supports_tty(stream)
