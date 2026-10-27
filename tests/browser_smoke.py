"""Load the actual WebAssembly build in mobile Chromium."""
import functools
import http.server
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

handler = functools.partial(
    http.server.SimpleHTTPRequestHandler,
    directory=str(Path("webapp/build/web").resolve()),
)
server = http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2, is_mobile=True, has_touch=True,
        )
        page = context.new_page()
        messages = []
        page.on("console", lambda msg: messages.append(msg.text))
        page.on("pageerror", lambda err: messages.append(str(err)))
        try:
            page.goto("http://127.0.0.1:8000", wait_until="domcontentloaded")
            # The runtime deliberately waits for a user gesture.
            page.touchscreen.tap(195, 420)
            page.wait_for_function(
                """() => {
                    const canvas = document.querySelector('#canvas');
                    const info = document.querySelector('#infobox');
                    return canvas && canvas.width >= 300 && info &&
                        getComputedStyle(info).display === 'none';
                }""",
                timeout=180000,
            )
            page.touchscreen.tap(195, 420)
            page.wait_for_timeout(1000)
            page.set_viewport_size({"width": 844, "height": 390})
            page.wait_for_timeout(1000)
            assert page.locator("#canvas").evaluate(
                "canvas => getComputedStyle(canvas).touchAction"
            ) == "none"
            errors = [m for m in messages if
                      "Traceback (most recent call last)" in m or
                      "ModuleNotFoundError" in m or "SyntaxError" in m]
            assert not errors, errors
            print("Mobile Chromium: WebAssembly started, touch enabled, rotation completed.")
        finally:
            print("\n".join(messages[-60:]))
            browser.close()
finally:
    server.shutdown()
