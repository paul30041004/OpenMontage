#!/usr/bin/env python3
"""flow-shorts — Google Flow browser automation harness.

Minimal CDP client over the Chrome DevTools Protocol using only the Python
standard library (websocket framing implemented locally) plus `requests` for
the /json endpoint handshake. No third-party websocket packages required.

The harness is intentionally stateless between calls: every script below
opens a connection to the debug port, runs, and returns JSON on stdout.
State that must survive between runs (image id -> Flow card title mapping)
is persisted in <state_dir>/state.json by the caller-facing scripts.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import socket
import struct
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SELECTORS_PATH = HERE / "selectors.json"


def load_selectors() -> dict[str, Any]:
    with open(SELECTORS_PATH, encoding="utf-8") as f:
        return json.load(f)


class CDPWebSocket:
    """Tiny CDP client — RFC6455 client framing (no masking key requirement is
    relaxed: Chrome accepts masked frames, which we send)."""

    def __init__(self, ws_url: str, timeout: float = 90.0):
        self.ws_url = ws_url
        parsed = urllib.parse.urlparse(ws_url)  # type: ignore[attr-defined]
        self.host = parsed.hostname or "127.0.0.1"
        self.port = parsed.port or 9222
        self.path = parsed.path
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        self.sock.settimeout(timeout)
        self._handshake()
        self._msg_id = 0
        self._recv_buf = b""

    def _handshake(self) -> None:
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("websocket handshake failed")
            resp += chunk
        if b"101" not in resp.split(b"\r\n")[0]:
            raise RuntimeError(f"websocket handshake rejected: {resp[:200]!r}")

    def _send_frame(self, payload: bytes) -> None:
        header = bytearray([0x81])  # FIN + text
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
        self.sock.sendall(bytes(header) + masked)

    def _recv_exact(self, n: int) -> bytes:
        while len(self._recv_buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("connection closed")
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

    def send(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._msg_id += 1
        msg = {"id": self._msg_id, "method": method, "params": params or {}}
        self._send_frame(json.dumps(msg).encode())
        while True:
            data = json.loads(self._read_frame().decode())
            if data.get("id") == self._msg_id:
                if "error" in data:
                    raise RuntimeError(f"{method}: {data['error']}")
                return data.get("result", {})

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass


class FlowHarness:
    """High-level operations against a Flow tab in a debug Chrome."""

    NAV_TIMEOUT = 30
    SETTLE_DELAY = 2.0

    def __init__(self, ws_url: str, screenshots_dir: Path):
        self.ws = CDPWebSocket(ws_url)
        self.screenshots_dir = screenshots_dir
        self.selectors = load_selectors()
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.ws.send("Runtime.enable")
        self.ws.send("Page.enable")

    def close(self) -> None:
        self.ws.close()

    # -- low-level helpers ---------------------------------------------------

    def eval_js(self, expr: str) -> Any:
        res = self.ws.send(
            "Runtime.evaluate",
            {"expression": expr, "returnByValue": True, "awaitPromise": True},
        )
        if res.get("exceptionDetails"):
            raise RuntimeError(f"JS error: {res['exceptionDetails']}")
        return res.get("result", {}).get("value")

    def screenshot(self, name: str) -> Path:
        ts = time.strftime("%H%M%S")
        path = self.screenshots_dir / f"{ts}_{name}.png"
        res = self.ws.send(
            "Page.captureScreenshot", {"format": "png"}
        )
        with open(path, "wb") as f:
            f.write(base64.b64decode(res["data"]))
        return path

    def node_from_ref(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Resolve a {css} | {tag,text_regex,attr} | {js} selector spec to a
        Runtime.RemoteObject node ref via Runtime.evaluate + DOM.requestNode."""
        if "css" in spec:
            expr = f"document.querySelector({json.dumps(spec['css'])})"
            node = self._node_for_expr(expr)
        elif "tag" in spec:
            regex = spec["text_regex"].replace('"', '\\"')
            attr = spec.get("attr")
            attr_clause = f"&& el.getAttribute('{attr}')" if attr else ""
            if attr:
                match_clause = (
                    f"(el.textContent.match(/{regex}/) || "
                    f"el.getAttribute('{attr}').match(/{regex}/))"
                )
            else:
                match_clause = f"el.textContent.match(/{regex}/)"
            expr = (
                "Array.from(document.getElementsByTagName("
                f"'{spec['tag']}')).find(el => {match_clause}{attr_clause})"
            )
            node = self._node_for_expr(expr)
        else:
            raise ValueError(f"selector spec must have css or tag: {spec}")
        if node is None:
            raise LookupError(f"no element matched spec: {spec}")
        return node

    def _node_for_expr(self, expr: str) -> dict[str, Any] | None:
        res = self.ws.send(
            "Runtime.evaluate",
            {"expression": f"({expr}) ? ({expr}) : null", "returnByValue": False},
        )
        if res.get("exceptionDetails"):
            raise RuntimeError(f"JS error in {expr}: {res['exceptionDetails']}")
        obj = res.get("result", {})
        if obj.get("type") == "null" or obj.get("subtype") == "null":
            return None
        node_res = self.ws.send("DOM.requestNode", {"objectId": obj["objectId"]})
        return node_res["node"]

    def click_node(self, node: dict[str, Any]) -> None:
        remote = self.ws.send("DOM.resolveNode", {"nodeId": node["nodeId"]})
        object_id = remote["object"]["objectId"]
        self.ws.send(
            "Runtime.callFunctionOn",
            {
                "objectId": object_id,
                "functionDeclaration": (
                    "function(){ this.scrollIntoView({block:'center'}); "
                    "this.dispatchEvent(new MouseEvent('pointerdown',{bubbles:true}));"
                    "this.dispatchEvent(new MouseEvent('mousedown',{bubbles:true}));"
                    "this.dispatchEvent(new MouseEvent('pointerup',{bubbles:true}));"
                    "this.dispatchEvent(new MouseEvent('mouseup',{bubbles:true}));"
                    "this.click(); }"
                ),
                "returnByValue": True,
            },
        )

    def type_into_node(self, node: dict[str, Any], text: str) -> None:
        remote = self.ws.send("DOM.resolveNode", {"nodeId": node["nodeId"]})
        object_id = remote["object"]["objectId"]
        self.ws.send(
            "Runtime.callFunctionOn",
            {
                "objectId": object_id,
                "functionDeclaration": (
                    "function(text){ this.focus(); "
                    "this.value = text; "
                    "this.dispatchEvent(new Event('input',{bubbles:true})); "
                    "this.dispatchEvent(new Event('change',{bubbles:true})); }"
                ),
                "arguments": [{"value": text}],
                "returnByValue": True,
            },
        )

    def set_file_input(self, node: dict[str, Any], file_path: Path) -> None:
        """Attach a local file to an <input type=file> via DOM.setFileInputFiles."""
        self.ws.send(
            "DOM.setFileInputFiles",
            {"files": [str(file_path.resolve())], "nodeId": node["nodeId"]},
        )

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)

    # -- Flow operations -----------------------------------------------------

    # ---- settings-panel helpers (calibrated against flow.google.com,
    # ---- Angular Material UI, Sep 2026). Real mouse clicks at element
    # ---- coordinates are REQUIRED — JS .click() misses Angular bindings.

    def _mouse_click_center(self, js_expr: str) -> str:
        """Evaluate js_expr -> {x,y} | error-string, and click at coords."""
        res = self.ws.send("Runtime.evaluate",
                           {"expression": js_expr, "returnByValue": True})
        v = res.get("result", {}).get("value")
        if not isinstance(v, str):
            return f"bad-return: {v!r}"
        if not v.startswith("{"):
            return v
        box = json.loads(v)
        if box.get("x", 0) == 0 and box.get("y", 0) == 0:
            return "zero-coords (element hidden?)"
        self.ws.send("Input.dispatchMouseEvent",
                     {"type": "mousePressed", "x": box["x"], "y": box["y"],
                      "button": "left", "clickCount": 1})
        self.ws.send("Input.dispatchMouseEvent",
                     {"type": "mouseReleased", "x": box["x"], "y": box["y"],
                      "button": "left", "clickCount": 1})
        return "clicked"

    def _panel_open(self) -> bool:
        return bool(self.eval_js("!!document.querySelector('.settings-content')"))

    def _open_settings_panel(self, timeout: float = 8.0) -> None:
        if self._panel_open():
            return
        try:
            self.ws.send("Page.bringToFront")
        except Exception:
            pass
        deadline = time.time() + timeout
        while time.time() < deadline:
            r = self._mouse_click_center("""(() => {
              const b = Array.from(document.querySelectorAll('button')).find(
                x => /Nano Banana|crop_|Video ·|Image ·|Veo/.test(x.textContent));
              if (!b) return 'no-chip';
              const r = b.getBoundingClientRect();
              return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2});
            })()""")
            if r != "clicked":
                raise LookupError(f"settings chip not clickable: {r}")
            poll_deadline = time.time() + 2.5
            while time.time() < poll_deadline:
                if self._panel_open():
                    return
                time.sleep(0.3)
        raise LookupError("settings panel did not open")

    def _close_settings_panel(self, timeout: float = 5.0) -> None:
        if not self._panel_open():
            return
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.ws.send("Input.dispatchKeyEvent",
                         {"type": "keyDown", "key": "Escape", "code": "Escape",
                          "windowsVirtualKeyCode": 27})
            self.ws.send("Input.dispatchKeyEvent",
                         {"type": "keyUp", "key": "Escape", "code": "Escape",
                          "windowsVirtualKeyCode": 27})
            poll_deadline = time.time() + 1.5
            while time.time() < poll_deadline:
                if not self._panel_open():
                    return
                time.sleep(0.3)

    def _click_settings_toggle(self, label: str) -> None:
        """Click a mat-button-toggle inside the settings panel by its label
        ('Image', 'Video', '9:16', '4s', 'x1', ...)."""
        r = self._mouse_click_center(f"""(() => {{
          const sc = document.querySelector('.settings-content');
          if (!sc) return 'no-panel';
          const btn = Array.from(sc.querySelectorAll('.mat-button-toggle-button'))
            .find(b => {{
              const lines = b.innerText.trim().split('\\n').map(s => s.trim());
              return lines.includes('{label}') || b.innerText.trim() === '{label}';
            }});
          if (!btn) return 'toggle-not-found: {label}';
          const toggle = btn.closest('mat-button-toggle');
          if (toggle && toggle.classList.contains('mat-button-toggle-checked')) {{
            return 'already-checked';
          }}
          btn.scrollIntoView({{block: 'center'}});
          const r = btn.getBoundingClientRect();
          return JSON.stringify({{x: r.x + r.width/2, y: r.y + r.height/2}});
        }})()""")
        if r not in ("clicked", "already-checked"):
            raise LookupError(f"toggle {label}: {r}")
        self.wait(1.2)

    def _open_model_menu_and_select(self, model_name: str) -> None:
        curr = self.eval_js("""(() => {
          const sc = document.querySelector('.settings-content');
          if (!sc) return '';
          const b = Array.from(sc.querySelectorAll('button'))
            .find(x => /arrow_drop_down/.test(x.textContent));
          return b ? b.textContent : '';
        })()""") or ""
        if model_name in curr:
            return

        r = self._mouse_click_center("""(() => {
          const sc = document.querySelector('.settings-content');
          if (!sc) return 'no-panel';
          const b = Array.from(sc.querySelectorAll('button'))
            .find(x => /arrow_drop_down/.test(x.textContent));
          if (!b) return 'no-model-btn';
          const r = b.getBoundingClientRect();
          return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2});
        })()""")
        if r != "clicked":
            raise LookupError(f"model dropdown: {r}")
        self.wait(2.0)
        model_js = json.dumps(model_name)
        r = self._mouse_click_center(f"""(() => {{
          const items = Array.from(document.querySelectorAll('cdk-overlay-container *'))
            .filter(e => e.textContent && e.textContent.includes({model_js}) && e.children.length === 0);
          const item = items[items.length - 1];
          if (!item) return 'model-not-found: ' + Array.from(document.querySelectorAll('cdk-overlay-container *')).filter(e => e.children.length===0 && e.textContent.trim()).slice(0,10).map(e=>e.textContent.trim().slice(0,30)).join('/');
          const target = item.closest('button, mat-option, [role=menuitem], [class*=option]') || item;
          const r = target.getBoundingClientRect();
          return JSON.stringify({{x: r.x + r.width/2, y: r.y + r.height/2}});
        }})()""")
        if r != "clicked":
            raise LookupError(f"select model {model_name}: {r}")
        self.wait(1.5)

    def _read_credits_line(self) -> str:
        return self.eval_js("""(() => {
          const sc = document.querySelector('.settings-content');
          if (!sc) return '';
          const m = sc.innerText.match(/Generating will use ([^\\n]+)/i);
          return m ? m[1] : sc.innerText.slice(-60);
        })()""") or ""

    def _peek_credits_line(self) -> str:
        """Read the credits line without leaving the panel open state changed."""
        return self._read_credits_line()

    def _type_prompt(self, prompt: str) -> None:
        res = self.ws.send("Runtime.evaluate", {"expression": """(() => {
          const pm = document.querySelector('.ProseMirror');
          if (!pm) return 'no-pm';
          pm.focus();
          document.execCommand('selectAll', false, null);
          document.execCommand('delete', false, null);
          return 'cleared';
        })()""", "returnByValue": True})
        if res.get("result", {}).get("value") != "cleared":
            raise LookupError("ProseMirror prompt box not found")
        self.wait(0.3)
        res = self.ws.send("Runtime.evaluate", {"expression": f"""(() => {{
          document.execCommand('insertText', false, {json.dumps(prompt)});
          return document.querySelector('.ProseMirror').textContent.length;
        }})()""", "returnByValue": True})
        typed = res.get("result", {}).get("value")
        # placeholder text inflates length; just require it to be non-trivial
        if not isinstance(typed, int) or typed < len(prompt) // 2:
            raise RuntimeError(f"prompt typing failed (len={typed})")

    def _click_create(self) -> None:
        r = self._mouse_click_center("""(() => {
          const b = Array.from(document.querySelectorAll('button'))
            .find(x => x.textContent.trim() === 'arrow_forward' && !x.disabled);
          if (!b) return 'no-create-btn';
          const r = b.getBoundingClientRect();
          return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2});
        })()""")
        if r != "clicked":
            raise LookupError(f"create button: {r}")

    def _count_videos(self) -> int:
        return self.eval_js("document.querySelectorAll('video').length") or 0

    def _count_large_images(self) -> int:
        return self.eval_js(
            "Array.from(document.querySelectorAll('img'))"
            ".filter(i => (i.naturalWidth||i.width) >= 256).length"
        ) or 0

    def _wait_for_new_video(self, before: int, timeout: float = 1800.0):
        """Single-variant convenience wrapper around _wait_for_new_videos."""
        results = self._wait_for_new_videos(before, n=1, timeout=timeout)
        return results[0] if results else None

    def _wait_for_new_videos(self, before: int, n: int, timeout: float = 2400.0):
        """Wait for `n` NEW video elements AND no progress indicator, then
        return [(url, width, height, duration), ...] (may be fewer than n if
        Flow coalesces variants). Flow activates <flow-video-tile> on hover,
        so we hover each tile in the virtual grid to obtain the signed video URLs.
        Lower-priority generations stall at fixed percentages for minutes —
        that is normal queue behavior. Returns [] on timeout."""
        deadline = time.time() + timeout
        last_report = 0.0
        start_time = time.time()
        while time.time() < deadline:
            state = self.eval_js("""(() => {
              const vids = document.querySelectorAll('video').length;
              const prog = (document.body.innerText.match(/\\d+%/g) || []).slice(-1);
              return JSON.stringify({vids, prog});
            })()""")
            s = json.loads(state or '{}')
            now = time.time()
            if now - last_report > 30:
                print(json.dumps({"waiting": True, "videos": s.get('vids'),
                                  "need": before + n,
                                  "progress": (s.get('prog') or [None])[-1]},
                                 ensure_ascii=False), flush=True)
                last_report = now

            # When progress indicator disappears after initial startup, probe tiles
            if not s.get("prog") and (now - start_time > 15):
                tiles_res = self.eval_js("""(() => {
                  const tiles = Array.from(document.querySelectorAll('.tile-row > FLOW-GRID-TILE-CONTAINER, .tile-row > *'));
                  return JSON.stringify(tiles.slice(0, 10).map((t, i) => {
                    const r = t.getBoundingClientRect();
                    return {idx: i, x: r.x + r.width/2, y: r.y + r.height/2};
                  }));
                })()""")
                tile_coords = json.loads(tiles_res or '[]')
                out = []
                for coord in tile_coords[:n]:
                    self.ws.send("Input.dispatchMouseEvent",
                                 {"type": "mouseMoved", "x": coord["x"], "y": coord["y"]})
                    time.sleep(1.2)
                    vinfo = self.eval_js(f"""(() => {{
                      const tiles = Array.from(document.querySelectorAll('.tile-row > FLOW-GRID-TILE-CONTAINER, .tile-row > *'));
                      const t = tiles[{coord['idx']}];
                      const v = t ? t.querySelector('video') : null;
                      if (!v) return null;
                      return JSON.stringify({{
                        src: v.src || (v.querySelector('source')||{{}}).src || null,
                        w: v.videoWidth || 720,
                        h: v.videoHeight || 1280,
                        dur: v.duration || 8
                      }});
                    }})()""")
                    if vinfo:
                        d = json.loads(vinfo)
                        if d.get("src"):
                            out.append((d["src"], d["w"], d["h"], d["dur"]))

                if len(out) >= n:
                    return out
                elif len(out) > 0 and (now - start_time > 120):
                    return out

            time.sleep(8)
        return []

    def _attach_reference_image(self, file_path: Path) -> None:
        """Attach a reference image via the Ingredients button + file input.
        Requires the settings panel flow to be completed first."""
        r = self._mouse_click_center("""(() => {
          const sc = document.querySelector('.settings-content');
          const root = sc || document;
          const b = Array.from(root.querySelectorAll('button'))
            .find(x => /Ingredients|재료/.test(x.textContent));
          if (!b) return 'no-ingredients-btn';
          const r = b.getBoundingClientRect();
          return JSON.stringify({x: r.x + r.width/2, y: r.y + r.height/2});
        })()""")
        if r != "clicked":
            raise LookupError(f"ingredients button: {r}")
        self.wait(2.0)
        # after clicking Ingredients there may be an upload affordance; try
        # a file input in overlays or the main document
        found = self.eval_js("""(() => {
          const inputs = Array.from(document.querySelectorAll('input[type=file]'));
          return inputs.length;
        })()""")
        if not found:
            raise LookupError("no file input appeared after Ingredients click — "
                              "reference attach flow needs manual calibration")
        node = self.node_from_ref({"css": "input[type=file]"})
        self.set_file_input(node, file_path)
        self.wait(2.0)

    def get_card_titles(self) -> list[str]:
        js = self.selectors["card_titles"]["js"]
        return self.eval_js(js) or []

    def wait_for_new_card_title(self, existing: list[str], timeout: float = 180.0) -> str | None:
        """Return the first new card title that appears, or None on timeout.
        Card-title counting is the most break-resistant completion signal
        (filenames don't exist, URL patterns move, list is virtualized)."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            titles = self.get_card_titles()
            for t in titles:
                if t not in existing:
                    return t
            time.sleep(3)
        return None

    def get_asset_url(self, title: str) -> str | None:
        js = self.selectors["asset_url"]["js"].replace("{title}", json.dumps(title))
        return self.eval_js(js)

    def download_asset(self, url: str, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
            return dest
        except Exception:
            # Fallback: in-page fetch utilizing browser session cookies
            b64 = self.eval_js(f"""(async () => {{
              const resp = await fetch({json.dumps(url)});
              if (!resp.ok) return null;
              const blob = await resp.blob();
              const buf = await blob.arrayBuffer();
              const bytes = new Uint8Array(buf);
              let binary = '';
              for (let i = 0; i < bytes.length; i += 8192) {{
                binary += String.fromCharCode.apply(null, bytes.subarray(i, i + 8192));
              }}
              return btoa(binary);
            }})()""")
            if b64:
                with open(dest, "wb") as f:
                    f.write(base64.b64decode(b64))
                return dest
            raise


# -- CLI entrypoints ---------------------------------------------------------


def get_ws_url(port: int, flow_url: str) -> str:
    """Find (or open) a tab showing Flow; return its webSocketDebuggerUrl."""
    tabs = json.loads(
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5).read()
    )
    flow_tabs = [t for t in tabs if t.get("type") == "page" and "flow" in (t.get("url") or "")]
    if flow_tabs:
        return flow_tabs[0]["webSocketDebuggerUrl"]
    # open a new tab
    tab = json.loads(
        urllib.request.urlopen(
            f"http://127.0.0.1:{port}/json/new?{flow_url}", timeout=5
        ).read()
    )
    return tab["webSocketDebuggerUrl"]


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    port = int(os.environ.get("FLOW_DEBUG_PORT", "9222"))
    flow_url = os.environ.get("FLOW_URL", "https://labs.google/fx/ko/tools/flow")

    if cmd == "check":
        try:
            tabs = json.loads(
                urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5).read()
            )
            flow_tabs = [t for t in tabs if t.get("type") == "page" and "flow" in (t.get("url") or "")]
            print(json.dumps({"ok": True, "port": port, "flow_tabs": len(flow_tabs)}, ensure_ascii=False))
        except Exception as e:  # noqa: BLE001
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
            sys.exit(1)
    else:
        print(json.dumps({"error": f"unknown command {cmd}"}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()