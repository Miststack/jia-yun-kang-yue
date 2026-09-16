# -*- coding: utf-8 -*-
"""甲韵康跃 · 监测与预警系统 桌面入口。窗口标题和尺寸来自 app/config.json。"""

from __future__ import annotations

import base64
import json
import os
import queue
import re
import subprocess
import sys
import threading
from pathlib import Path

import serial
import webview
from serial.tools import list_ports

NUMBER_RE = re.compile(r"\d+\.?\d*")


def app_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def load_config() -> dict:
    path = app_dir() / "app" / "config.json"
    return json.loads(path.read_text(encoding="utf-8"))


def user_state_dir(short_name: str) -> Path:
    root = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
    path = root / short_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def records_dir(short_name: str) -> Path:
    path = Path.home() / "Documents" / f"{short_name}监测记录"
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_window_bounds(short_name: str) -> dict | None:
    path = user_state_dir(short_name) / "window.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def save_window_bounds(short_name: str, width: int, height: int) -> None:
    path = user_state_dir(short_name) / "window.json"
    path.write_text(
        json.dumps({"width": int(width), "height": int(height)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


class SerialWorker:
    def __init__(self, read_timeout: float = 0.05) -> None:
        self._q: queue.Queue[float] = queue.Queue()
        self._lock = threading.Lock()
        self._ser: serial.Serial | None = None
        self._running = False
        self._buffer = ""
        self.port_name = ""
        self._read_timeout = read_timeout

    def list_ports(self) -> list[dict[str, str]]:
        items = []
        for port in list_ports.comports():
            items.append(
                {
                    "device": port.device,
                    "description": port.description or port.device,
                }
            )
        return items

    def connect(self, port: str, baudrate: int = 9600) -> dict:
        self.disconnect()
        try:
            ser = serial.Serial(port, int(baudrate), timeout=self._read_timeout)
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
        with self._lock:
            self._ser = ser
            self._running = True
            self._buffer = ""
            self.port_name = port
        threading.Thread(target=self._loop, daemon=True).start()
        return {"ok": True, "port": port}

    def disconnect(self) -> dict:
        with self._lock:
            self._running = False
            ser = self._ser
            self._ser = None
            self.port_name = ""
        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass
        return {"ok": True}

    def status(self) -> dict:
        with self._lock:
            connected = self._ser is not None and self._running
            port = self.port_name
        return {"connected": connected, "port": port}

    def poll(self) -> list[float]:
        values: list[float] = []
        while True:
            try:
                values.append(self._q.get_nowait())
            except queue.Empty:
                break
        return values

    def _loop(self) -> None:
        while True:
            with self._lock:
                if not self._running or self._ser is None:
                    break
                ser = self._ser
            try:
                waiting = ser.in_waiting
                chunk = ser.read(waiting if waiting else 1)
            except Exception:
                break
            if not chunk:
                continue
            self._buffer += chunk.decode("utf-8", errors="ignore")
            lines = self._buffer.split("\n")
            self._buffer = lines.pop() if lines else ""
            for line in lines:
                for num in NUMBER_RE.findall(line.strip()):
                    try:
                        val = float(num)
                    except ValueError:
                        continue
                    if val > 0:
                        self._q.put(val)


class Api:
    def __init__(self, worker: SerialWorker, short_name: str) -> None:
        self.worker = worker
        self.window = None
        self.short_name = short_name

    def list_ports(self):
        return self.worker.list_ports()

    def connect_serial(self, port, baudrate=9600):
        return self.worker.connect(port, baudrate)

    def disconnect_serial(self):
        return self.worker.disconnect()

    def serial_status(self):
        return self.worker.status()

    def poll_serial(self):
        return self.worker.poll()

    def set_on_top(self, enabled=True):
        if self.window is not None:
            self.window.on_top = bool(enabled)
        return {"ok": True, "on_top": bool(enabled)}

    def toggle_fullscreen(self):
        if self.window is not None:
            self.window.toggle_fullscreen()
        return {"ok": True}

    def save_text_file(self, filename, content):
        name = Path(str(filename or "监测记录.csv")).name
        path = records_dir(self.short_name) / name
        path.write_text(str(content or ""), encoding="utf-8-sig")
        return {"ok": True, "path": str(path)}

    def save_image_file(self, filename, data_url):
        name = Path(str(filename or "波形.png")).name
        raw = str(data_url or "")
        if "," in raw:
            raw = raw.split(",", 1)[1]
        path = records_dir(self.short_name) / name
        path.write_bytes(base64.b64decode(raw))
        return {"ok": True, "path": str(path)}

    def open_records_folder(self):
        path = records_dir(self.short_name)
        try:
            os.startfile(str(path))  # type: ignore[attr-defined]
        except Exception:
            subprocess.Popen(["explorer", str(path)])
        return {"ok": True, "path": str(path)}

    def save_window_size(self, width, height):
        try:
            save_window_bounds(self.short_name, int(width), int(height))
        except Exception:
            return {"ok": False}
        return {"ok": True}


def main() -> None:
    cfg = load_config()
    if not getattr(sys, "frozen", False):
        try:
            sys.path.insert(0, str(app_dir()))
            from apply_config import write_branding_bat, write_config_js

            write_config_js(cfg)
            write_branding_bat(cfg)
        except Exception:
            pass
    brand = cfg.get("branding", {})
    win = cfg.get("window", {})
    serial_cfg = cfg.get("serial", {})
    ui_cfg = cfg.get("ui") or {}
    short_name = brand.get("short_name") or "监测系统"
    worker = SerialWorker(read_timeout=float(serial_cfg.get("read_timeout", 0.05)))
    api = Api(worker, short_name)
    index = app_dir() / "app" / "index.html"
    if not index.exists():
        raise FileNotFoundError(f"找不到界面文件: {index}")

    width = int(win.get("width", 1480))
    height = int(win.get("height", 940))
    if ui_cfg.get("remember_window", True):
        saved = load_window_bounds(short_name)
        if saved:
            width = max(int(win.get("min_width", 1080)), int(saved.get("width") or width))
            height = max(int(win.get("min_height", 720)), int(saved.get("height") or height))

    window = webview.create_window(
        brand.get("app_name", "监测与预警系统"),
        str(index),
        width=width,
        height=height,
        min_size=(int(win.get("min_width", 1080)), int(win.get("min_height", 720))),
        js_api=api,
        background_color=win.get("background", "#0a0d1a"),
        text_select=True,
        maximized=False,
    )
    api.window = window
    if bool(ui_cfg.get("on_top_default", False)):
        window.on_top = True

    def on_resized(*args):
        if not ui_cfg.get("remember_window", True):
            return
        try:
            w = args[0] if len(args) >= 1 else getattr(window, "width", None)
            h = args[1] if len(args) >= 2 else getattr(window, "height", None)
            if w and h:
                save_window_bounds(short_name, int(w), int(h))
        except Exception:
            pass

    def on_closing():
        try:
            if ui_cfg.get("auto_save_on_close", True):
                snap = window.evaluate_js(
                    "window.__csvSnapshot ? JSON.stringify(window.__csvSnapshot()) : null"
                )
                if snap:
                    payload = json.loads(snap) if isinstance(snap, str) else snap
                    if payload and payload.get("text"):
                        api.save_text_file(payload.get("name") or "autosave.csv", payload["text"])
            if ui_cfg.get("confirm_close"):
                dirty = window.evaluate_js(
                    "window.__hasUnsaved ? !!window.__hasUnsaved() : false"
                )
                if dirty:
                    ok = window.evaluate_js('confirm("还有本段数据。关闭前已尝试保存到记录夹。确定关闭？")')
                    if ok is False or ok == "false":
                        return False
        except Exception:
            pass
        return True

    try:
        window.events.resized += on_resized
    except Exception:
        pass
    try:
        window.events.closing += on_closing
    except Exception:
        pass
    window.events.closed += worker.disconnect

    debug = "--debug" in sys.argv
    try:
        webview.start(debug=debug, gui="edgechromium")
    except Exception:
        webview.start(debug=debug)


if __name__ == "__main__":
    main()
