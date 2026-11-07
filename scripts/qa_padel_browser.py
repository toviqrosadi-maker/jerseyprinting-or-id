"""Final Chromium QA. Requires an existing Playwright + Chromium installation.

Run with the Python interpreter containing Playwright:
    python scripts/qa_padel_browser.py --output <evidence-directory>
The server binds an ephemeral localhost port; WhatsApp requests are intercepted.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import json
import traceback
import argparse
import runpy
import tempfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=None)
args=parser.parse_args()
OUT=args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='padel-browser-qa-'))
OUT.mkdir(parents=True,exist_ok=True)
PAGES=['jersey-padel-custom.html','bahan-jersey-padel.html','desain-jersey-padel-custom.html','checklist-pesan-jersey-padel-custom.html','index.html']

class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
results=[]
anchor_results=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--disable-logging'])
        print('Browser:',browser.version,flush=True)
        for width in [1440,390]:
            context=browser.new_context(viewport={'width':width,'height':1000 if width==1440 else 844},device_scale_factor=1)
            context.route('https://wa.me/**',lambda route:route.fulfill(status=200,content_type='text/html',body='<title>WhatsApp intercepted locally for QA</title>'))
            for name in PAGES:
                page=context.new_page()
                item={'page':name,'viewport':width,'failures':[]}
                console=[]
                page.on('pageerror',lambda error:console.append(str(error)))
                try:
                    response=page.goto(BASE+name,wait_until='networkidle')
                    item['http_status']=response.status
                    if response.status!=200:item['failures'].append('Page HTTP status')
                    # Trigger lazy images before checking and capturing the full page.
                    page.evaluate("async () => { for (const img of document.images) { img.loading='eager'; } await Promise.all([...document.images].map(i=>i.decode().catch(()=>{}))); }")
                    item['layout']=page.evaluate("""() => ({
                        viewport:innerWidth, documentWidth:document.documentElement.scrollWidth,
                        horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,
                        overflowingElements:[...document.querySelectorAll('body *')].filter(e=>{
                            const s=getComputedStyle(e), r=e.getBoundingClientRect();
                            return s.display!=='none' && s.visibility!=='hidden' && r.width>0 && (r.left< -1 || r.right>innerWidth+1);
                        }).slice(0,20).map(e=>({tag:e.tagName,class:e.className,text:e.textContent.trim().slice(0,60)})),
                        images:[...document.images].map(e=>({src:e.getAttribute('src'),alt:e.alt,
                            loaded:e.complete&&e.naturalWidth>0,natural:[e.naturalWidth,e.naturalHeight],
                            rendered:[e.getBoundingClientRect().width,e.getBoundingClientRect().height],objectFit:getComputedStyle(e).objectFit})),
                        paragraphs:[...document.querySelectorAll('.article p')].slice(0,4).map(e=>({fontSize:getComputedStyle(e).fontSize,lineHeight:getComputedStyle(e).lineHeight,width:e.getBoundingClientRect().width})),
                        headings:[...document.querySelectorAll('main h1, .article h2, .article h3')].map(e=>({level:e.tagName,text:e.textContent,clipped:e.scrollWidth>e.clientWidth+1,fontSize:getComputedStyle(e).fontSize})),
                        waLinks:[...document.querySelectorAll('a[href*="wa.me"]')].map(e=>({text:e.textContent.trim(),href:e.href,visible:!!e.getClientRects().length}))
                    })""")
                    if item['layout']['horizontalOverflow']:item['failures'].append('Horizontal overflow')
                    if any(not i['loaded'] for i in item['layout']['images']):item['failures'].append('Broken image')
                    if any(h['clipped'] for h in item['layout']['headings']):item['failures'].append('Clipped heading')
                    if any('wa.me/6281221111398' not in a['href'] for a in item['layout']['waLinks']):item['failures'].append('Wrong WhatsApp number')
                    if any(float(x['fontSize'].replace('px',''))<16 for x in item['layout']['paragraphs']):item['failures'].append('Paragraph below 16px')
                    prefix=f'{name.removesuffix(".html")}-{width}'
                    page.screenshot(path=str(OUT/f'{prefix}-hero.jpg'),type='jpeg',quality=82)
                    item['screenshots']=[f'{prefix}-hero.jpg']
                    if name!='index.html':
                        page.locator('.article').scroll_into_view_if_needed()
                        page.screenshot(path=str(OUT/f'{prefix}-article.jpg'),type='jpeg',quality=82)
                        item['screenshots'].append(f'{prefix}-article.jpg')
                        article=page.locator('article.article')
                        item['article_images']=article.locator('img').count()
                        item['article_homepage_anchor']=article.locator('a[href="/"]').filter(has_text='jersey printing').count()
                        item['article_pillar_links']=article.locator('a[href="/jersey-padel-custom.html"]').count()
                        if item['article_homepage_anchor']!=1:item['failures'].append('Missing exact homepage anchor')
                        if name!='jersey-padel-custom.html' and item['article_pillar_links']<1:item['failures'].append('Missing pillar link')
                        local=article.locator('a[href^="/"]').evaluate_all('(links)=>[...new Set(links.map(a=>a.getAttribute("href")))]')
                        item['local_link_statuses']={href:page.request.get(BASE.rstrip('/')+href).status for href in local}
                        if any(s!=200 for s in item['local_link_statuses'].values()):item['failures'].append('Broken contextual link')
                        # Verify a contextual link is actually navigable, not just present.
                        expected=article.locator('a[href^="/"]').first.get_attribute('href')
                        article.locator('a[href^="/"]').first.click()
                        page.wait_for_load_state('networkidle')
                        item['contextual_click_url']=page.url
                        if page.url!=BASE.rstrip('/')+expected:item['failures'].append('Contextual link click destination')
                        page.goto(BASE+name,wait_until='networkidle')
                    else:
                        card=page.locator('#produk .sport-card').filter(has=page.get_by_role('heading',name='Jersey Padel',exact=True))
                        link=card.get_by_role('link',name='Lihat Detail')
                        item['padel_card_href']=link.get_attribute('href')
                        if item['padel_card_href']!='/jersey-padel-custom.html':item['failures'].append('Padel card href')
                        card.scroll_into_view_if_needed()
                        page.screenshot(path=str(OUT/f'{prefix}-padel-card.jpg'),type='jpeg',quality=82)
                        item['screenshots'].append(f'{prefix}-padel-card.jpg')
                        link.click()
                        page.wait_for_load_state('networkidle')
                        item['padel_card_click_url']=page.url
                        if page.url!=BASE+'jersey-padel-custom.html':item['failures'].append('Padel card click destination')
                        page.goto(BASE+name,wait_until='networkidle')
                    # Test mobile navigation open/close and an actual navigation target.
                    if width==390:
                        menu=page.get_by_role('button',name='Buka menu')
                        menu.click()
                        item['mobile_menu_opens']=page.locator('.navlinks').is_visible()
                        page.locator('.navlinks').get_by_role('link',name='Jenis Jersey').click()
                        page.wait_for_load_state('networkidle')
                        item['mobile_nav_url']=page.url
                        item['mobile_menu_closes_after_navigation']=not page.locator('.navlinks').is_visible()
                        if not item['mobile_menu_opens'] or not item['mobile_menu_closes_after_navigation']:item['failures'].append('Mobile menu behavior')
                        if not page.url.endswith('index.html#produk'):item['failures'].append('Mobile navigation destination')
                        page.goto(BASE+name,wait_until='networkidle')
                    else:
                        item['desktop_nav_visible']=page.locator('.navlinks').is_visible()
                        if not item['desktop_nav_visible']:item['failures'].append('Desktop navigation hidden')
                    wa=page.locator('.mobile-cta') if width==390 else page.locator('.hero-actions a[href*="wa.me"]').first
                    with page.expect_popup() as popup_info:
                        wa.click()
                    popup=popup_info.value
                    popup.wait_for_load_state('domcontentloaded')
                    item['whatsapp_click_url']=popup.url
                    item['whatsapp_intercepted_locally']=popup.title()=='WhatsApp intercepted locally for QA'
                    if not item['whatsapp_intercepted_locally']:item['failures'].append('WhatsApp popup intercept')
                    popup.close()
                    if name=='jersey-padel-custom.html':
                        faq=page.locator('details.faq').first
                        faq.locator('summary').click()
                        item['faq_opens']=faq.get_attribute('open') is not None and faq.locator('p').is_visible()
                        if not item['faq_opens']:item['failures'].append('FAQ cannot open')
                    item['page_errors']=console
                    if console:item['failures'].append('JavaScript error')
                except Exception as error:
                    item['failures'].append(str(error))
                    item['traceback']=traceback.format_exc()
                finally:
                    results.append(item)
                    page.close()
                    print(name,width,'PASS' if not item['failures'] else 'FAIL',item['failures'],flush=True)
            context.close()
        # Regression test for the bug found during final QA: sticky header covered
        # destination headings after clicking the in-page table of contents.
        all_new=runpy.run_path(str(ROOT/'scripts/qa_padel.py'))['NEW']
        for width in [1440,390]:
            page=browser.new_page(viewport={'width':width,'height':1000 if width==1440 else 844})
            for name in all_new:
                page.goto(BASE+name,wait_until='networkidle')
                for selector in ['.hero-actions a[href="#panduan"]','.toc a[href^="#"]']:
                    link=page.locator(selector).first
                    href=link.get_attribute('href')
                    link.click()
                    page.evaluate('''async () => { let stable=0, previous=-1; for(let i=0;i<200;i++){await new Promise(requestAnimationFrame); let now=scrollY; stable=Math.abs(now-previous)<.1?stable+1:0;previous=now;if(stable>8)break;} }''')
                    measure=page.evaluate('''href=>{const t=document.querySelector(href).getBoundingClientRect(), h=document.querySelector('.site-header').getBoundingClientRect();return {targetTop:t.top,headerBottom:h.bottom,visibleBelowHeader:t.top>=h.bottom-1}}''',href)
                    measure.update(page=name,viewport=width,anchor=href)
                    anchor_results.append(measure)
                    if name=='jersey-padel-custom.html' and href!='#panduan':
                        page.screenshot(path=str(OUT/f'pillar-{width}-anchor-after.jpg'),type='jpeg',quality=82)
                print('Anchors:',name,width,'PASS' if all(x['visibleBelowHeader'] for x in anchor_results if x['page']==name and x['viewport']==width) else 'FAIL',flush=True)
            page.close()
        browser.close()
finally:
    server.shutdown()
    (OUT/'browser-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'anchor-results.json').write_text(json.dumps(anchor_results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Results:',OUT/'browser-results.json',flush=True)
raise SystemExit(any(x['failures'] for x in results) or any(not x['visibleBelowHeader'] for x in anchor_results))
