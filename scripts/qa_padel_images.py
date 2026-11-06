"""Audit existing padel images without modifying website files or image assets.

Requires an installed Playwright + Chromium. Run:
    python scripts/qa_padel_images.py --output <evidence-directory>
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import argparse
import hashlib
import json
import runpy
import subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
OUT = args.output.resolve()
OUT.mkdir(parents=True, exist_ok=True)
NEW = runpy.run_path(str(ROOT / 'scripts/qa_padel.py'))['NEW']


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{server.server_port}/'
cases, inventory, failures = [], [], []
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--disable-logging'])
        version = browser.version
        # Decode every source asset, including possible higher-resolution copies
        # under a different filename. Screenshots in docs are not source assets.
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.goto(BASE, wait_until='networkidle')
        files = sorted(path for path in (ROOT / 'assets').rglob('*')
                       if path.suffix.lower() in {'.webp', '.png', '.jpg', '.jpeg', '.avif'})
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            data = page.evaluate('''async url => {
                const img=new Image(); img.src=url;
                try {await img.decode();return {width:img.naturalWidth,height:img.naturalHeight,loaded:true};}
                catch {return {loaded:false};}
            }''', BASE + relative)
            data.update(file=relative, bytes=path.stat().st_size,
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            inventory.append(data)
            if not data['loaded']:
                failures.append(f'Asset decode failed: {relative}')
        # Source-image contact sheet for visual matching; no asset editing.
        cards = ''.join(
            f'<figure><img src="{BASE}{item["file"]}"><figcaption>{item["file"].split("/")[-1]}<br>'
            f'{item.get("width")} × {item.get("height")} · {item["bytes"]} B</figcaption></figure>'
            for item in inventory)
        page.set_content('''<!doctype html><html><head><meta charset="utf-8"><style>
            body{background:#171a18;color:#fff;font:13px Arial;margin:20px}
            main{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}
            figure{margin:0;padding:8px;background:#252a26}img{width:100%;height:145px;object-fit:contain}
            figcaption{overflow-wrap:anywhere;line-height:1.4}</style></head><body><main>'''+cards+'</main></body></html>')
        page.evaluate('async () => await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))')
        page.screenshot(path=str(OUT / 'source-assets-contact-sheet.jpg'), full_page=True, type='jpeg', quality=88)
        page.close()
        for width in [1440, 390]:
            for dpr in [1, 2]:
                context = browser.new_context(viewport={'width': width, 'height': 1000 if width == 1440 else 844},
                                              device_scale_factor=dpr)
                for name in NEW:
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    response = page.goto(BASE + name, wait_until='networkidle')
                    page.evaluate('async () => await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))')
                    data = page.evaluate('''() => {
                        const image = e => {
                            const r=e.getBoundingClientRect(), c=getComputedStyle(e);
                            return {src:e.getAttribute('src'),currentSrc:new URL(e.currentSrc).pathname,
                              srcset:e.getAttribute('srcset'),sizes:e.getAttribute('sizes'),
                              naturalWidth:e.naturalWidth,naturalHeight:e.naturalHeight,
                              renderedWidth:r.width,renderedHeight:r.height,
                              devicePixelsNeeded:[r.width*devicePixelRatio,r.height*devicePixelRatio],
                              densityAvailable:e.naturalWidth/r.width,
                              cssUpscale:e.naturalWidth<r.width-1,
                              insufficientForDpr:e.naturalWidth<r.width*devicePixelRatio-1,
                              loaded:e.complete&&e.naturalWidth>0,objectFit:c.objectFit,
                              cssWidth:c.width,cssHeight:c.height,filter:c.filter,
                              transform:c.transform,imageRendering:c.imageRendering,
                              widthAttribute:e.getAttribute('width'),heightAttribute:e.getAttribute('height')};
                        };
                        return {viewport:innerWidth,dpr:devicePixelRatio,
                          documentWidth:document.documentElement.scrollWidth,
                          horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,
                          hero:image(document.querySelector('.cluster-hero-media img')),
                          inlineArticleImages:[...document.querySelectorAll('article.article img')].map(image),
                          allImagesLoaded:[...document.images].every(i=>i.complete&&i.naturalWidth>0),
                          responsivePictureSources:document.querySelectorAll('picture source').length,
                          h1Count:document.querySelectorAll('h1').length};
                    }''')
                    data.update(page=name, httpStatus=response.status, pageErrors=errors)
                    if response.status != 200 or not data['allImagesLoaded'] or errors or data['horizontalOverflow']:
                        failures.append(f'Layout/loading failure: {name}, {width}px, DPR {dpr}')
                    if name == 'jersey-padel-custom.html':
                        prefix=f'pillar-{width}-dpr{dpr}'
                        page.screenshot(path=str(OUT/f'{prefix}-hero.jpg'), type='jpeg', quality=92)
                        # Center the complete figure so the fixed mobile CTA does
                        # not overlap it in the element screenshot.
                        page.locator('.cluster-hero-media').evaluate("el => el.scrollIntoView({block:'center',behavior:'instant'})")
                        page.locator('.cluster-hero-media').screenshot(path=str(OUT/f'{prefix}-image.png'))
                    cases.append(data)
                    page.close()
                context.close()
                print(f'{len(NEW)} pages: {width}px, DPR {dpr}: loading/layout checked', flush=True)
        browser.close()
finally:
    server.shutdown()

source = 'assets/images/product-padel-new.webp'
current = next(item for item in inventory if item['file'] == source)
same_hash = [item['file'] for item in inventory if item['sha256'] == current['sha256']]
history = subprocess.check_output(['git','log','--all','--format=%h %s','--',source,
                                  'assets/images/product-padel.webp'],cwd=ROOT,text=True).splitlines()
report = {'browser':version,'source':current,'byteIdenticalCopies':same_hash,
          'assetHistory':history,'assetInventory':inventory,'cases':cases,'failures':failures}
(OUT/'image-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'source':current,'cases':len(cases),'inventory':len(inventory),
                  'pillar':[case for case in cases if case['page']=='jersey-padel-custom.html'],
                  'failures':failures},ensure_ascii=False,indent=2),flush=True)
raise SystemExit(bool(failures))
