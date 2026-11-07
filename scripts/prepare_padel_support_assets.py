"""Convert/install supplied support-article hero images, preserving all other HTML.

Requires existing Playwright + Chromium. All variants preserve the source ratio.
python scripts/prepare_padel_support_assets.py --output <manifest.json>
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import quote
import argparse
import base64
import hashlib
import json
import re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SIZES = '(max-width: 850px) calc(92vw - 2px), (max-width: 1283px) 40vw, 482px'
ASSETS = [
    ('03 — Bahan Jersey Padel.jpg', 'bahan-jersey-padel', 'Memeriksa sampel kain untuk jersey padel di samping jersey dan raket'),
    ('04 — Desain Jersey Padel Custom.jpg', 'desain-jersey-padel-custom', 'Desainer menyiapkan pola jersey padel custom dengan contoh warna dan kain'),
    ('05 — Ukuran Jersey Padel Pria dan Wanita.jpg', 'ukuran-jersey-padel-pria-wanita', 'Pengukuran lebar dada jersey padel pria dengan pemain wanita di sampingnya'),
    ('06 — Jersey Padel Full Printing Sublimasi.jpg', 'jersey-padel-full-printing-sublimasi', 'Pemeriksaan jersey padel full printing di dekat mesin press sublimasi'),
    ('07 — Jersey Padel Komunitas.jpg', 'jersey-padel-komunitas', 'Anggota komunitas padel mengenakan jersey senada sambil membawa raket'),
    ('08 — Jersey Padel Turnamen.jpg', 'jersey-padel-turnamen', 'Pasangan pemain memakai jersey tim dalam pertandingan padel'),
    ('09 — Jersey Padel Lengan Panjang atau Pendek.jpg', 'jersey-padel-lengan-panjang-pendek', 'Dua pemain padel membandingkan jersey lengan pendek dan lengan panjang'),
    ('10 — Jersey Padel Nama, Logo dan Sponsor.jpg', 'jersey-padel-nama-logo-sponsor', 'Tampilan depan dan belakang jersey padel dengan area nama, logo, dan sponsor'),
    ('11 — Cara Merawat Jersey Padel.jpg', 'cara-merawat-jersey-padel', 'Mencuci jersey padel dengan tangan di dekat rak pengering pakaian'),
    ('12 — Checklist Pesan Jersey Padel Custom.jpg', 'checklist-pesan-jersey-padel-custom', 'Persiapan pesanan jersey padel dengan sampel kain, meteran, desain, dan checklist'),
]


def hero_tag(slug, alt, width=1376, height=768):
    prefix='/assets/images/'+slug
    return (f'<img src="{prefix}.webp" srcset="{prefix}-688.webp 688w, {prefix}-1032.webp 1032w, {prefix}.webp 1376w" '
            f'sizes="{SIZES}" alt="{alt}" width="{width}" height="{height}" loading="eager" fetchpriority="high" decoding="async"/>')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self,*args): pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'assets/images')))
    Thread(target=server.serve_forever,daemon=True).start()
    records=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--disable-logging'])
            page=browser.new_page()
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            for source,slug,alt in ASSETS:
                variants=page.evaluate('''async url=>{
                    const img=new Image();img.src=url;await img.decode();
                    if(img.naturalWidth!==1376||img.naturalHeight!==768)throw Error('Unexpected source dimensions; review variants before resizing');
                    return [1376,1032,688].map(width=>{
                        const canvas=document.createElement('canvas');canvas.width=width;canvas.height=width*24/43;
                        const ctx=canvas.getContext('2d');ctx.imageSmoothingQuality='high';ctx.drawImage(img,0,0,canvas.width,canvas.height);
                        const data=canvas.toDataURL('image/webp',.95);if(!data.startsWith('data:image/webp;base64,'))throw Error('No WebP encoder');
                        return {width:canvas.width,height:canvas.height,data:data.split(',')[1]};
                    });
                }''',quote(source))
                record={'source':source,'page':slug+'.html','source_bytes':(ROOT/'assets/images'/source).stat().st_size,
                        'source_sha256':hashlib.sha256((ROOT/'assets/images'/source).read_bytes()).hexdigest(),'quality':.95,'variants':[]}
                for variant in variants:
                    filename=slug+('' if variant['width']==1376 else '-'+str(variant['width']))+'.webp'
                    payload=base64.b64decode(variant.pop('data'))
                    (ROOT/'assets/images'/filename).write_bytes(payload)
                    record['variants'].append(dict(file=filename,bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest(),**variant))
                path=ROOT/(slug+'.html')
                text=path.read_text(encoding='utf-8')
                text,count=re.subn(r'(<figure class="cluster-hero-media">)<img\b[^>]*>',lambda m:m[1]+hero_tag(slug,alt),text,count=1)
                assert count==1,slug
                path.write_text(text,encoding='utf-8')
                records.append(record)
                print(slug,record['variants'][0]['bytes'],flush=True)
            browser.close()
    finally:
        server.shutdown()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':
    main()
