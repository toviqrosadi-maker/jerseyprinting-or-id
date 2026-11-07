"""Release QA: 11 cluster pages, responsive heroes, metadata regression and CLS.

python scripts/qa_padel_support_release.py --output <evidence-directory>
Requires installed Playwright and Chromium; never contacts production.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import argparse
import hashlib
import json
import re
import runpy
import subprocess
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
OUT=parser.parse_args().output.resolve()
OUT.mkdir(parents=True,exist_ok=True)
qa=runpy.run_path(str(ROOT/'scripts/qa_padel.py'))
config=runpy.run_path(str(ROOT/'scripts/prepare_padel_support_assets.py'))
expected={slug+'.html':config['hero_tag'](slug,alt) for _,slug,alt in config['ASSETS']}
failures=[]
for name in subprocess.check_output(['git','ls-tree','-r','--name-only','4348dd4'],cwd=ROOT,text=True).splitlines():
    if not (name.endswith('.html') or name in ['sitemap.xml','robots.txt','vercel.json','assets/css/style.css','assets/css/padel.css','assets/js/main.js']):continue
    before=subprocess.check_output(['git','show','4348dd4:'+name],cwd=ROOT).decode('utf-8').replace('\r\n','\n')
    after=(ROOT/name).read_text(encoding='utf-8')
    if name in expected:
        pattern=r'(<figure class="cluster-hero-media">)(<img\b[^>]*>)'
        actual=re.search(pattern,after).group(2)
        if actual!=expected[name]:failures.append(name+': hero does not match mapping')
        before_tag=re.search(pattern,before).group(2)
        after=re.sub(pattern,lambda m:m[1]+before_tag,after,count=1)
    if name=='assets/css/padel.css':
        ratio_rule='''\n/* Reserve the source ratio before decoding to prevent image layout shifts. */
.cluster-hero-media img[width="1376"][height="768"],
.article .padel-cta img[width="1376"][height="768"] {
  aspect-ratio: 1376 / 768;
}
'''
        after=after.replace(ratio_rule,'')
    if after!=before:failures.append(name+': unexpected change outside hero/ratio reservation')

class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
cases=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--disable-logging'])
        for width in [1440,390]:
            for dpr in [1,2]:
                context=browser.new_context(viewport={'width':width,'height':1000 if width==1440 else 844},device_scale_factor=dpr)
                context.add_init_script('''window.qaShifts=[];new PerformanceObserver(list=>{
                    for(const e of list.getEntries())if(!e.hadRecentInput)window.qaShifts.push({value:e.value,time:e.startTime});
                }).observe({type:'layout-shift',buffered:true});''')
                for name in qa['NEW']:
                    page=context.new_page()
                    errors=[]
                    page.on('pageerror',lambda error:errors.append(str(error)))
                    # Exercise reserved layout space with delayed image delivery.
                    page.route('**/assets/images/*.webp',lambda route:(page.wait_for_timeout(120),route.continue_()))
                    response=page.goto(BASE+name,wait_until='networkidle')
                    page.locator('.cluster-hero-media img').evaluate('async e=>await e.decode()')
                    initial_cls=page.evaluate('window.qaShifts.reduce((s,e)=>s+e.value,0)')
                    if dpr==1:
                        page.screenshot(path=str(OUT/f'{name[:-5]}-{width}-hero.jpg'),type='jpeg',quality=82)
                    page.locator('.cluster-hero-media').evaluate("e=>e.scrollIntoView({block:'center',behavior:'instant'})")
                    if dpr==2 and width==390:
                        page.locator('.cluster-hero-media').screenshot(path=str(OUT/f'{name[:-5]}-390-dpr2-image.png'))
                    # Exercise all late-loaded images and the bottom of the page.
                    page.evaluate("() => {for(const e of document.images)e.loading='eager';}")
                    page.evaluate('async()=>await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))')
                    page.evaluate('()=>scrollTo({top:document.body.scrollHeight,behavior:"instant"})')
                    page.wait_for_timeout(200)
                    result=page.evaluate('''async()=>{
                        const e=document.querySelector('.cluster-hero-media img'),r=e.getBoundingClientRect(),s=getComputedStyle(e);
                        const actual=new Image();actual.src=e.currentSrc;await actual.decode();
                        const links=[...document.querySelectorAll('article.article a')];
                        return {viewport:innerWidth,dpr:devicePixelRatio,documentWidth:document.documentElement.scrollWidth,
                            src:e.getAttribute('src'),currentSrc:new URL(e.currentSrc).pathname,
                            sourcePixels:[actual.naturalWidth,actual.naturalHeight],rendered:[r.width,r.height],
                            ratioDifference:Math.abs(r.width/r.height-actual.naturalWidth/actual.naturalHeight),objectFit:s.objectFit,
                            width:e.getAttribute('width'),height:e.getAttribute('height'),loading:e.loading,priority:e.fetchPriority,
                            enoughForDpr:actual.naturalWidth>=r.width*devicePixelRatio-1,
                            allImagesLoaded:[...document.images].every(i=>i.complete&&i.naturalWidth>0),
                            cls:window.qaShifts.reduce((s,e)=>s+e.value,0),shifts:window.qaShifts,
                            homepageAnchors:links.filter(a=>a.getAttribute('href')==='/'&&a.textContent.trim()==='jersey printing').length,
                            pillarLinks:links.filter(a=>a.getAttribute('href')==='/jersey-padel-custom.html').length};
                    }''')
                    result.update(page=name,httpStatus=response.status,pageErrors=errors,initialCls=initial_cls)
                    problems=[]
                    if response.status!=200 or errors or not result['allImagesLoaded']:problems.append('Loading/JS')
                    if result['documentWidth']>width+1:problems.append('Horizontal overflow')
                    if result['ratioDifference']>.002 or result['objectFit']!='contain':problems.append('Crop/distortion')
                    if not result['enoughForDpr']:problems.append('Insufficient pixel density')
                    if result['cls']>.001:problems.append('Unexpected layout shift')
                    if result['homepageAnchors']!=1 or name!='jersey-padel-custom.html' and result['pillarLinks']<1:problems.append('Cluster links')
                    if result['priority']!='high' or not result['width'] or not result['height']:problems.append('Image attributes')
                    result['failures']=problems
                    failures.extend(f'{name} {width}px DPR{dpr}: {problem}' for problem in problems)
                    cases.append(result)
                    page.close()
                context.close()
                print(width,dpr,'11 pages checked',flush=True)
        browser.close()
finally:
    server.shutdown()
report={'baseline':'4348dd4','cases':cases,'failures':failures}
(OUT/'release-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'cases':len(cases),'maxCLS':max(c['cls'] for c in cases),'failures':failures},ensure_ascii=False,indent=2),flush=True)
raise SystemExit(bool(failures))
