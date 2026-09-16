# -*- coding: utf-8 -*-
"""甲韵康跃 · 监测与预警系统 桌面入口。"""

from __future__ import annotations

import queue
import re
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


class SerialWorker:
    def __init__(self) -> None:
        self._q: queue.Queue[float] = queue.Queue()
        self._lock = threading.Lock()
        self._ser: serial.Serial | None = None
        self._running = False
        self._buffer = ""
        self.port_name = ""

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
            ser = serial.Serial(port, int(baudrate), timeout=0.05)
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
    def __init__(self, worker: SerialWorker) -> None:
        self.worker = worker

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


def main() -> None:
    worker = SerialWorker()
    index = app_dir() / "app" / "index.html"
    if not index.exists():
        raise FileNotFoundError(f"找不到界面文件: {index}")

    window = webview.create_window(
        "甲韵康跃 · 监测与预警系统",
        str(index),
        width=1480,
        height=940,
        min_size=(1080, 720),
        js_api=Api(worker),
        background_color="#0a0d1a",
        text_select=True,
        maximized=False,
    )
    window.events.closed += worker.disconnect

    debug = "--debug" in sys.argv
    try:
        webview.start(debug=debug, gui="edgechromium")
    except Exception:
        webview.start(debug=debug)


if __name__ == "__main__":
    main()
