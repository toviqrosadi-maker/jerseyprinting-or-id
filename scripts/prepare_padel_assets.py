"""Convert the two supplied JPG assets to WebP without resizing or cropping.

Requires the existing Playwright + Chromium installation. No backup writes.
Run: python scripts/prepare_padel_assets.py
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import base64
import hashlib
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / 'assets/images'
FILES = [
    ('Man_holding_padel_racket_b5165b84.jpg', 'jersey-padel-custom-hero.webp'),
    ('Custom_padel_jersey_banner_design_f9e218c5.jpg', 'jersey-padel-custom-cta.webp'),
]


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(IMAGES)))
Thread(target=server.serve_forever, daemon=True).start()
records = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-logging'])
        page = browser.new_page()
        page.goto(f'http://127.0.0.1:{server.server_port}/')
        for source, target in FILES:
            encoded = page.evaluate('''async name => {
                const img = new Image(); img.src = name; await img.decode();
                const canvas = document.createElement('canvas');
                canvas.width = img.naturalWidth; canvas.height = img.naturalHeight;
                canvas.getContext('2d').drawImage(img, 0, 0);
                const data = canvas.toDataURL('image/webp', 0.95);
                if (!data.startsWith('data:image/webp;base64,')) throw Error('WebP encoder unavailable');
                return {width:canvas.width,height:canvas.height,data:data.split(',')[1]};
            }''', source)
            output = base64.b64decode(encoded.pop('data'))
            (IMAGES / target).write_bytes(output)
            records.append(dict(source=source, output=target, **encoded,
                                source_bytes=(IMAGES / source).stat().st_size,
                                output_bytes=len(output), webp_quality=0.95,
                                source_sha256=hashlib.sha256((IMAGES / source).read_bytes()).hexdigest(),
                                output_sha256=hashlib.sha256(output).hexdigest()))
        browser.close()
finally:
    server.shutdown()
print(json.dumps(records, ensure_ascii=False, indent=2))
