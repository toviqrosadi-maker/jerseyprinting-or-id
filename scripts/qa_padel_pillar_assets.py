"""QA for supplied pillar hero/CTA assets, including WhatsApp click interception.

Run with a Python interpreter containing Playwright:
    python scripts/qa_padel_pillar_assets.py --output <evidence-directory>
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit, parse_qs
import argparse
import hashlib
import json
import runpy
import subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
OUT = parser.parse_args().output.resolve()
OUT.mkdir(parents=True, exist_ok=True)


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{server.server_port}/'
results, failures, assets = [], [], []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-logging'])
        # Source/output decode dimensions and bytes; verify no resize.
        probe = browser.new_page()
        probe.goto(BASE)
        for source, output in [
            ('Man_holding_padel_racket_b5165b84.jpg','jersey-padel-custom-hero.webp'),
            ('Custom_padel_jersey_banner_design_f9e218c5.jpg','jersey-padel-custom-cta.webp'),
        ]:
            paths = ['assets/images/'+source, 'assets/images/'+output]
            sizes = probe.evaluate('''async paths => await Promise.all(paths.map(async path=>{
                const img=new Image(); img.src=path; await img.decode();
                return [img.naturalWidth,img.naturalHeight];
            }))''', paths)
            assets.append({'source':source,'webp':output,'source_dimensions':sizes[0],
                'webp_dimensions':sizes[1], 'source_bytes':(ROOT/paths[0]).stat().st_size,
                'webp_bytes':(ROOT/paths[1]).stat().st_size,
                'source_sha256':hashlib.sha256((ROOT/paths[0]).read_bytes()).hexdigest(),
                'webp_sha256':hashlib.sha256((ROOT/paths[1]).read_bytes()).hexdigest()})
            if sizes[0] != sizes[1]:
                failures.append('Source/output dimensions changed: '+output)
        probe.close()
        for width in [1440,390]:
            for dpr in [1,2]:
                context = browser.new_context(viewport={'width':width,'height':1000 if width==1440 else 844},device_scale_factor=dpr)
                context.route('https://wa.me/**',lambda route:route.fulfill(status=200,content_type='text/html',body='<title>Local WhatsApp QA</title>'))
                page = context.new_page()
                errors = []
                page.on('pageerror',lambda error:errors.append(str(error)))
                response = page.goto(BASE+'jersey-padel-custom.html',wait_until='networkidle')
                page.locator('.cluster-hero-media img').evaluate('async img => await img.decode()')
                prefix=f'pillar-{width}-dpr{dpr}'
                page.screenshot(path=str(OUT/f'{prefix}-hero.jpg'),type='jpeg',quality=90)
                page.locator('.cluster-hero-media').evaluate("el=>el.scrollIntoView({block:'center',behavior:'instant'})")
                page.locator('.cluster-hero-media').screenshot(path=str(OUT/f'{prefix}-hero-image.png'))
                cta = page.locator('.padel-cta-link')
                cta.evaluate("el=>el.scrollIntoView({block:'center',behavior:'instant'})")
                cta.locator('img').evaluate('async img => await img.decode()')
                page.screenshot(path=str(OUT/f'{prefix}-cta-context.jpg'),type='jpeg',quality=90)
                cta.screenshot(path=str(OUT/f'{prefix}-cta.png'))
                data = page.evaluate('''() => {
                    const measure = selector => {
                        const e=document.querySelector(selector),r=e.getBoundingClientRect(),s=getComputedStyle(e);
                        const ratio=e.naturalWidth/e.naturalHeight;
                        return {src:e.getAttribute('src'),naturalWidth:e.naturalWidth,naturalHeight:e.naturalHeight,
                            renderedWidth:r.width,renderedHeight:r.height,loaded:e.complete&&e.naturalWidth>0,
                            ratioDifference:Math.abs(r.width/r.height-ratio),objectFit:s.objectFit,
                            maxHeight:s.maxHeight,loading:e.loading,fetchpriority:e.getAttribute('fetchpriority'),
                            width:e.getAttribute('width'),height:e.getAttribute('height'),alt:e.alt};
                    };
                    const cta=document.querySelector('.padel-cta-link'),caption=cta.querySelector('figcaption'),s=getComputedStyle(caption);
                    const order=[...document.querySelector('article.article').children];
                    const index=order.indexOf(cta);
                    const preceding=order.slice(0,index).filter(e=>e.tagName==='H2').pop();
                    return {viewport:innerWidth,dpr:devicePixelRatio,documentWidth:document.documentElement.scrollWidth,
                        hero:measure('.cluster-hero-media img'),banner:measure('.padel-cta img'),
                        captionFont:s.fontSize,captionText:caption.textContent,
                        captionWraps:caption.scrollWidth<=caption.clientWidth+1,
                        phoneSingleLine:cta.querySelector('.padel-cta-phone').getClientRects().length===1,
                        ctaHref:cta.href,previousSection:preceding.id,
                        nextSection:order[index+1].id,
                        h1Count:document.querySelectorAll('h1').length,
                        canonical:document.querySelector('link[rel=canonical]').href,
                        ogImage:document.querySelector('meta[property="og:image"]').content};
                }''')
                data['httpStatus'] = response.status
                data['pageErrors'] = errors
                case_errors = []
                if response.status!=200 or errors:case_errors.append('Loading/JS')
                if data['documentWidth']>width+1:case_errors.append('Horizontal overflow')
                for kind in ['hero','banner']:
                    image=data[kind]
                    if not image['loaded'] or image['ratioDifference']>.005 or image['objectFit']!='contain':case_errors.append(kind+' cropped/distorted')
                    if not image['alt'] or not image['width'] or not image['height']:case_errors.append(kind+' missing attributes')
                if data['hero']['loading']!='eager' or data['hero']['fetchpriority']!='high':case_errors.append('Hero priority')
                if data['banner']['loading']!='lazy':case_errors.append('Banner not lazy')
                if float(data['captionFont'].removesuffix('px'))<16 or not data['captionWraps'] or not data['phoneSingleLine']:case_errors.append('Caption readability')
                if '0812-2111-1398' not in data['captionText']:case_errors.append('Missing visible phone')
                if data['previousSection']!='desain-yang-menunjukkan-identitas-tanpa-mengurangi-keterbacaan':case_errors.append('CTA placement')
                url=urlsplit(data['ctaHref'])
                message=parse_qs(url.query).get('text',[''])[0]
                if url.netloc!='wa.me' or url.path!='/6281221111398' or 'jersey padel custom' not in message:case_errors.append('CTA destination/message')
                with page.expect_popup() as popup_info:
                    cta.click()
                popup=popup_info.value
                popup.wait_for_load_state('domcontentloaded')
                data['ctaClickUrl']=popup.url
                data['ctaIntercepted']=popup.title()=='Local WhatsApp QA'
                if not data['ctaIntercepted']:case_errors.append('CTA click')
                popup.close()
                data['failures']=case_errors
                results.append(data)
                failures.extend(f'{width}px DPR {dpr}: {error}' for error in case_errors)
                print(width,dpr,'PASS' if not case_errors else case_errors,flush=True)
                context.close()
        browser.close()
finally:
    server.shutdown()

# Compare all tracked HTML to the pre-installation commit. Only the requested
# pillar image attributes, OG image, and one new CTA block may differ.
q=runpy.run_path(str(ROOT/'scripts/qa_padel.py'))
old=subprocess.check_output(['git','show','4ad3f34:jersey-padel-custom.html'],cwd=ROOT).decode('utf-8').replace('\r\n','\n')
current=(ROOT/'jersey-padel-custom.html').read_text(encoding='utf-8')
before,after=q['parse'](old),q['parse'](current)
for selector in [('p',{}),('h1',{}),('h2',{})]:
    tag,attrs=selector
    if [e.text() for e in before.find(tag,**attrs)] != [e.text() for e in after.find(tag,**attrs)]:failures.append('Existing text changed: '+tag)
old_links=[a.attrs.get('href') for a in before.find('a')]
new_links=[a.attrs.get('href') for a in after.find('a') if a.attrs.get('class')!='padel-cta-link']
if old_links!=new_links:failures.append('Existing internal/navigation links changed')
for tag,attrs in [('title',{}),('meta',{'name':'description'}),('link',{'rel':'canonical'})]:
    if before.find(tag,**attrs)[0].attrs != after.find(tag,**attrs)[0].attrs or before.find(tag,**attrs)[0].text()!=after.find(tag,**attrs)[0].text():failures.append('SEO metadata changed: '+tag)
for name in subprocess.check_output(['git','ls-tree','-r','--name-only','4ad3f34'],cwd=ROOT,text=True).splitlines():
    if name.endswith('.html') and name!='jersey-padel-custom.html' or name in ['sitemap.xml','vercel.json','robots.txt','assets/css/style.css','assets/js/main.js']:
        previous=subprocess.check_output(['git','show','4ad3f34:'+name],cwd=ROOT).decode('utf-8').replace('\r\n','\n')
        if (ROOT/name).read_text(encoding='utf-8') != previous:failures.append('Protected file changed: '+name)
report={'assets':assets,'cases':results,'failures':failures}
(OUT/'pillar-assets-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'assets':assets,'cases':len(results),'failures':failures},ensure_ascii=False,indent=2),flush=True)
raise SystemExit(bool(failures))
