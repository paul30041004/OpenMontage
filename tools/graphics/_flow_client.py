"""Lightweight CDP client helper for Google Flow tools."""

from __future__ import annotations

import base64
import json
import os
import socket
import struct
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


class FlowClient:
    def __init__(self, port: int = 9222):
        self.port = port
        self.ws_url = self._get_tab_ws_url()
        self.ws = self._connect_ws()
        self._msg_id = 0
        self._recv_buf = b""
        self.ws_send("Runtime.enable")
        self.ws_send("Page.enable")

    def _get_tab_ws_url(self) -> str:
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/json")
        with urllib.request.urlopen(req, timeout=5) as r:
            tabs = json.loads(r.read().decode())
        flow_tabs = [t for t in tabs if t.get("type") == "page" and "flow.google" in (t.get("url") or "")]
        if flow_tabs:
            return flow_tabs[0]["webSocketDebuggerUrl"]
        # Fallback to any flow tab
        flow_tabs = [t for t in tabs if t.get("type") == "page" and "flow" in (t.get("url") or "")]
        if flow_tabs:
            return flow_tabs[0]["webSocketDebuggerUrl"]
        raise RuntimeError("No Google Flow tab open. Navigate to https://flow.google.com in debug Chrome.")

    def _connect_ws(self) -> socket.socket:
        parsed = urllib.parse.urlparse(self.ws_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or self.port
        path = parsed.path
        sock = socket.create_connection((host, port), timeout=30)
        sock.settimeout(30)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        sock.sendall(req.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = sock.recv(4096)
            if not chunk:
                raise RuntimeError("WebSocket handshake failed")
            resp += chunk
        return sock

    def _send_frame(self, payload: bytes) -> None:
        header = bytearray([0x81])
        mask = os.urandom(4)
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", length)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", length)
        header += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.ws.sendall(bytes(header) + masked)

    def _recv_exact(self, n: int) -> bytes:
        while len(self._recv_buf) < n:
            chunk = self.ws.recv(65536)
            if not chunk:
                raise RuntimeError("WebSocket closed")
            self._recv_buf += chunk
        out, self._recv_buf = self._recv_buf[:n], self._recv_buf[n:]
        return out

    def _read_frame(self) -> bytes:
        b1, b2 = self._recv_exact(2)
        length = b2 & 0x7F
        if length == 126:
            (length,) = struct.unpack(">H", self._recv_exact(2))
        elif length == 127:
            (length,) = struct.unpack(">Q", self._recv_exact(8))
        if b2 & 0x80:
            mask = self._recv_exact(4)
            data = self._recv_exact(length)
            return bytes(x ^ mask[i % 4] for i, x in enumerate(data))
        return self._recv_exact(length)

    def ws_send(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._msg_id += 1
        msg = {"id": self._msg_id, "method": method, "params": params or {}}
        self._send_frame(json.dumps(msg).encode())
        while True:
            data = json.loads(self._read_frame().decode())
            if data.get("id") == self._msg_id:
                if "error" in data:
                    raise RuntimeError(f"{method}: {data['error']}")
                return data.get("result", {})

    def eval_js(self, expr: str) -> Any:
        res = self.ws_send("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
        return res.get("result", {}).get("value")

    def mouse_click(self, js_expr: str) -> str:
        v = self.eval_js(js_expr)
        if not isinstance(v, str) or not v.startswith("{"):
            return str(v)
        box = json.loads(v)
        self.ws_send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": box["x"], "y": box["y"], "button": "left", "clickCount": 1})
        self.ws_send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": box["x"], "y": box["y"], "button": "left", "clickCount": 1})
        return "clicked"

    def _open_settings(self) -> None:
        if self.eval_js("!!document.querySelector('.settings-content')"):
            return
        self.mouse_click("""(() => {
          const b = Array.from(document.querySelectorAll('button')).find(x => /Nano Banana|crop_|Video ·|Image ·|Veo/.test(x.textContent));
          if (!b) return 'no-chip';
          const r = b.getBoundingClientRect();
          return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2});
        })()""")
        time.sleep(2)

    def _close_settings(self) -> None:
        if not self.eval_js("!!document.querySelector('.settings-content')"):
            return
        self.ws_send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Escape", "code": "Escape", "windowsVirtualKeyCode": 27})
        self.ws_send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Escape", "code": "Escape", "windowsVirtualKeyCode": 27})
        time.sleep(1.5)

    def _click_toggle(self, label: str) -> None:
        self.mouse_click(f"""(() => {{
          const sc = document.querySelector('.settings-content');
          if (!sc) return 'no-panel';
          const btn = Array.from(sc.querySelectorAll('.mat-button-toggle-button'))
            .find(b => {{
              const lines = b.innerText.trim().split('\\n').map(s => s.trim());
              return lines.includes('{label}') || b.innerText.trim() === '{label}';
            }});
          if (!btn) return 'toggle-not-found';
          const toggle = btn.closest('mat-button-toggle');
          if (toggle && toggle.classList.contains('mat-button-toggle-checked')) return 'already-checked';
          const r = btn.getBoundingClientRect();
          return JSON.stringify({{x: r.x + r.width/2, y: r.y + r.height/2}});
        }})()""")
        time.sleep(1)

    def ensure_image_mode(self, aspect_ratio: str = "9:16") -> None:
        # Switch sidebar to Images view to ensure new image tiles are visible
        self.mouse_click("""(() => {
          const item = Array.from(document.querySelectorAll('mat-list-item')).find(x => x.textContent.trim().startsWith('Images'));
          if (!item) return 'no-item';
          const r = item.getBoundingClientRect();
          return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2});
        })()""")
        time.sleep(1)

        self._open_settings()
        self._click_toggle("Image")
        if aspect_ratio in ("9:16", "16:9", "1:1", "4:3", "3:4"):
            self._click_toggle(aspect_ratio)
        self._click_toggle("x1")
        self._close_settings()

    def ensure_video_mode(self, aspect_ratio: str = "9:16", duration: str = "8s", batch: str = "x4") -> None:
        # Switch sidebar to Videos view
        self.mouse_click("""(() => {
          const item = Array.from(document.querySelectorAll('mat-list-item')).find(x => x.textContent.trim().startsWith('Videos'));
          if (!item) return 'no-item';
          const r = item.getBoundingClientRect();
          return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2});
        })()""")
        time.sleep(1)

        self._open_settings()
        self._click_toggle("Video")
        # Ensure Veo 3.1 - Lite [Lower Priority]
        curr_model = self.eval_js("""(() => {
          const sc = document.querySelector('.settings-content');
          const b = sc ? Array.from(sc.querySelectorAll('button')).find(x => /arrow_drop_down/.test(x.textContent)) : null;
          return b ? b.textContent : '';
        })()""") or ""
        if "Veo 3.1 - Lite [Lower Priority]" not in curr_model:
            self.mouse_click("""(() => {
              const sc = document.querySelector('.settings-content');
              const b = sc ? Array.from(sc.querySelectorAll('button')).find(x => /arrow_drop_down/.test(x.textContent)) : null;
              if (!b) return 'no-btn';
              const r = b.getBoundingClientRect();
              return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2});
            })()""")
            time.sleep(1.5)
            self.mouse_click("""(() => {
              const items = Array.from(document.querySelectorAll('cdk-overlay-container *')).filter(e => e.textContent && e.textContent.includes('Veo 3.1 - Lite [Lower Priority]') && e.children.length === 0);
              const item = items[items.length - 1];
              const target = item ? (item.closest('button, mat-option, [role=menuitem]') || item) : null;
              if (!target) return 'no-target';
              const r = target.getBoundingClientRect();
              return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2});
            })()""")
            time.sleep(1.5)

        self._click_toggle(aspect_ratio)
        self._click_toggle(duration)
        self._click_toggle(batch)
        self._close_settings()

    def generate_image(self, prompt: str, timeout: float = 180.0) -> str:
        # Record before URLs
        raw_before = self.eval_js("""(() => {
          return JSON.stringify(Array.from(document.querySelectorAll('img')).map(i => i.src).filter(s => s.includes('flow-content.google/image')));
        })()""")
        before_urls = set(json.loads(raw_before or "[]"))

        # Clear existing text cleanly
        self.eval_js("""(() => {
          const pm = document.querySelector('.ProseMirror');
          if (pm) {
            pm.focus();
            const sel = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(pm);
            sel.removeAllRanges();
            sel.addRange(range);
          }
        })()""")
        self.ws_send("Input.dispatchKeyEvent", {"type": "rawKeyDown", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        self.ws_send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        time.sleep(0.3)

        # Type prompt using CDP native Input.insertText
        self.ws_send("Input.insertText", {"text": prompt})
        time.sleep(0.6)

        # Click Create button
        clicked = self.eval_js("""(() => {
          const b = document.querySelector('.generate-icon-button') || Array.from(document.querySelectorAll('button')).find(x => x.textContent.trim() === 'arrow_forward' && !x.disabled);
          if (b && !b.disabled) {
            b.click();
            return 'clicked';
          }
          return 'no-btn';
        })()""")
        if clicked != "clicked":
            # Fallback to mouse click via coordinates
            self.mouse_click("""(() => {
              const b = document.querySelector('.generate-icon-button') || Array.from(document.querySelectorAll('button')).find(x => x.textContent.trim() === 'arrow_forward');
              if (!b) return 'no-btn';
              const r = b.getBoundingClientRect();
              return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2});
            })()""")

        deadline = time.time() + timeout
        time.sleep(5)
        while time.time() < deadline:
            state = self.eval_js("""(() => {
              const prog = (document.body.innerText.match(/\\d+%/g) || []).slice(-1);
              const imgs = Array.from(document.querySelectorAll('img')).map(i => i.src).filter(s => s.includes('flow-content.google/image'));
              return JSON.stringify({prog: prog[0] || null, imgs: imgs});
            })()""")
            s = json.loads(state or "{}")
            current_imgs = s.get("imgs", [])
            new_imgs = [u for u in current_imgs if u not in before_urls]
            if not s.get("prog") and new_imgs:
                return new_imgs[0]
            if not s.get("prog") and current_imgs and current_imgs[0] not in before_urls:
                return current_imgs[0]
            time.sleep(4)
        raise TimeoutError("Timed out waiting for image generation in Google Flow")

    def generate_video(self, prompt: str, variants: int = 4, timeout: float = 1200.0) -> list[dict[str, Any]]:
        # Clear existing text cleanly
        self.eval_js("""(() => {
          const pm = document.querySelector('.ProseMirror');
          if (pm) {
            pm.focus();
            const sel = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(pm);
            sel.removeAllRanges();
            sel.addRange(range);
          }
        })()""")
        self.ws_send("Input.dispatchKeyEvent", {"type": "rawKeyDown", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        self.ws_send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        time.sleep(0.3)

        # Type prompt using CDP native Input.insertText
        self.ws_send("Input.insertText", {"text": prompt})
        time.sleep(0.6)

        # Click Create button
        clicked = self.eval_js("""(() => {
          const b = document.querySelector('.generate-icon-button') || Array.from(document.querySelectorAll('button')).find(x => x.textContent.trim() === 'arrow_forward' && !x.disabled);
          if (b && !b.disabled) {
            b.click();
            return 'clicked';
          }
          return 'no-btn';
        })()""")
        if clicked != "clicked":
            self.mouse_click("""(() => {
              const b = document.querySelector('.generate-icon-button') || Array.from(document.querySelectorAll('button')).find(x => x.textContent.trim() === 'arrow_forward');
              if (!b) return 'no-btn';
              const r = b.getBoundingClientRect();
              return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2});
            })()""")

        deadline = time.time() + timeout
        start_time = time.time()
        time.sleep(5)
        while time.time() < deadline:
            prog_raw = self.eval_js("(document.body.innerText.match(/\\d+%/g) || []).slice(-1)[0] || null")
            if not prog_raw and (time.time() - start_time > 30):
                # Hover tiles to obtain signed video URLs
                out = []
                for idx in range(variants):
                    res = self.eval_js(f"""(() => {{
                      const tiles = Array.from(document.querySelectorAll('.tile-row > FLOW-GRID-TILE-CONTAINER'));
                      const t = tiles[{idx}];
                      if (!t) return null;
                      const r = t.getBoundingClientRect();
                      return JSON.stringify({{x: r.x + r.width/2, y: r.y + r.height/2}});
                    }})()""")
                    if not res:
                        continue
                    box = json.loads(res)
                    self.ws_send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": box["x"], "y": box["y"]})
                    time.sleep(1.2)
                    vinfo = self.eval_js(f"""(() => {{
                      const tiles = Array.from(document.querySelectorAll('.tile-row > FLOW-GRID-TILE-CONTAINER'));
                      const t = tiles[{idx}];
                      const v = t ? t.querySelector('video') : null;
                      if (!v) return null;
                      return JSON.stringify({{
                        url: v.src || (v.querySelector('source')||{{}}).src || null,
                        width: v.videoWidth || 720,
                        height: v.videoHeight || 1280,
                        duration: v.duration || 8
                      }});
                    }})()""")
                    if vinfo:
                        d = json.loads(vinfo)
                        if d.get("url"):
                            out.append(d)
                if len(out) >= variants or (len(out) > 0 and time.time() - start_time > 180):
                    return out
            time.sleep(8)
        raise TimeoutError("Timed out waiting for video generation in Google Flow")

    def download_asset(self, url: str, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                f.write(chunk)
        return dest
