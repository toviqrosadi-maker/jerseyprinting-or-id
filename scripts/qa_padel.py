"""Read-only SEO/content/link regression checks. Run: python scripts/qa_padel.py."""
from collections import defaultdict
from html.parser import HTMLParser
from itertools import combinations
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen
import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.jerseyprinting.or.id/'
PILLAR = 'jersey-padel-custom.html'
SUPPORT = [
    'bahan-jersey-padel.html', 'desain-jersey-padel-custom.html',
    'ukuran-jersey-padel-pria-wanita.html', 'jersey-padel-full-printing-sublimasi.html',
    'jersey-padel-komunitas.html', 'jersey-padel-turnamen.html',
    'jersey-padel-lengan-panjang-pendek.html', 'jersey-padel-nama-logo-sponsor.html',
    'cara-merawat-jersey-padel.html', 'checklist-pesan-jersey-padel-custom.html',
]
NEW = [PILLAR] + SUPPORT
LEGACY = ['printing-jersey-bandung.html', 'jasa-pembuatan-jersey-bandung.html',
          'bahan-jersey-full-printing.html', 'tips-desain-jersey-tim.html']

class Node:
    def __init__(self, tag='', attrs=None, parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs or []), parent, []
    def text(self):
        return ' '.join(c if isinstance(c, str) else c.text() for c in self.children)
    def find(self, tag=None, **attrs):
        result = []
        if (not tag or self.tag == tag) and all(
            (v in self.attrs.get(k, '').split() if k == 'class' else self.attrs.get(k) == v)
            for k, v in attrs.items()
        ):
            result.append(self)
        for c in self.children:
            if isinstance(c, Node):
                result.extend(c.find(tag, **attrs))
        return result

class Parser(HTMLParser):
    VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = self.current = Node()
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in self.VOID:
            self.current = node
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)
    def handle_endtag(self, tag):
        node = self.current
        while node.parent:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent
    def handle_data(self, data):
        self.current.children.append(data)

def parse(source):
    return Parser(source).root

def words(text):
    return re.findall(r'\b\w+(?:[-–]\w+)*\b', text.lower())

def local_target(source, url):
    u = urlsplit(url)
    if u.scheme or u.netloc:
        if u.netloc not in ('www.jerseyprinting.or.id', 'jerseyprinting.or.id'):
            return None
    if not u.path:
        target = source
    else:
        target = (ROOT/unquote(u.path).lstrip('/')) if u.path.startswith('/') else source.parent/unquote(u.path)
    if target.is_dir():
        target /= 'index.html'
    return target.resolve(), unquote(u.fragment)

def main():
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument('--http-base', help='Optional local preview URL, e.g. http://127.0.0.1:8765/')
    args = arguments.parse_args()
    errors = []
    def check(ok, message):
        if not ok:
            errors.append(message)
    pages = {p.name: parse(p.read_text(encoding='utf-8')) for p in ROOT.glob('*.html')}
    counts, titles, canonical, meta, article_texts = {}, defaultdict(list), defaultdict(list), {}, {}
    peer_links = {}
    for name, dom in pages.items():
        ts = dom.find('title')
        check(len(ts) == 1, f'{name}: title count')
        if ts:
            titles[ts[0].text().strip()].append(name)
        cs = dom.find('link', rel='canonical')
        if cs:
            check(len(cs) == 1, f'{name}: canonical count')
            url = cs[0].attrs.get('href','')
            canonical[url].append(name)
            check(url.startswith(BASE), f'{name}: canonical domain')
        if name not in NEW:
            continue
        check(bool(cs) and cs[0].attrs.get('href') == BASE+name, f'{name}: self canonical')
        ds = dom.find('meta', name='description')
        check(len(ds) == 1 and bool(ds[0].attrs.get('content')), f'{name}: description')
        if ds:
            meta[name] = len(ds[0].attrs['content'])
        check(len(dom.find('h1')) == 1, f'{name}: H1 count')
        ids = [n.attrs['id'] for n in dom.find() if 'id' in n.attrs]
        check(len(ids) == len(set(ids)), f'{name}: duplicate IDs')
        check(dom.find('meta', property='og:url')[0].attrs.get('content') == BASE+name, f'{name}: OG URL')
        check(bool(dom.find('meta', name='robots')) and
              dom.find('meta', name='robots')[0].attrs['content'] == 'index,follow,max-image-preview:large',
              f'{name}: indexability')
        article = dom.find('article', **{'class':'article'})[0]
        text = article.text()
        article_texts[name] = text
        counts[name] = len(words(text))
        low, high = (2000,2500) if name == PILLAR else (1200,1800)
        check(low <= counts[name] <= high, f'{name}: {counts[name]} words, expected {low}-{high}')
        links = article.find('a')
        check(any(a.attrs.get('href') == '/' and a.text().strip() == 'jersey printing' for a in links), f'{name}: homepage anchor')
        paths = {a.attrs.get('href','').lstrip('/') for a in links}
        if name != PILLAR:
            check(PILLAR in paths, f'{name}: link to pillar')
            peers = paths.intersection(SUPPORT)-{name}
            peer_links[name] = sorted(peers)
            check(2 <= len(peers) <= 4, f'{name}: peer link count {len(peers)}')
        else:
            check(set(SUPPORT).issubset(paths), 'pillar: missing support link')
        heading_levels = [int(n.tag[1]) for n in article.find() if re.fullmatch('h[2-6]',n.tag)]
        prev = 1
        for level in heading_levels:
            check(level <= prev+1, f'{name}: skipped heading level')
            prev = level
        for img in dom.find('img'):
            check(bool(img.attrs.get('alt','').strip()), f'{name}: missing alt')
        for script in dom.find('script', type='application/ld+json'):
            try:
                data=json.loads(script.text())
                check(data.get('url') == BASE+name, f'{name}: schema URL')
            except ValueError:
                check(False, f'{name}: invalid JSON-LD')
        for a in dom.find('a'):
            url=a.attrs.get('href','')
            if 'wa.me/' in url:
                check(urlsplit(url).path == '/6281221111398', f'{name}: WhatsApp number changed')
    for name in NEW:
        check(name in pages, f'missing page: {name}')
    for title, names in titles.items():
        check(len(names) == 1, f'duplicate title: {names}')
    for url, names in canonical.items():
        check(len(names) == 1, f'duplicate canonical: {names}')
    descriptions=[pages[n].find('meta', name='description')[0].attrs['content'] for n in NEW]
    check(len(set(descriptions)) == len(NEW), 'duplicate new meta descriptions')
    h1s=[pages[n].find('h1')[0].text() for n in NEW]
    check(len(set(h1s)) == len(NEW), 'duplicate new H1s')
    for name in LEGACY:
        article = pages[name].find('article', **{'class':'article'})[0]
        check(any(a.attrs.get('href') == '/'+PILLAR and a.parent.tag == 'p' for a in article.find('a')), f'{name}: contextual pillar link')
    # All local href/src, fragment destinations, srcset, inline CSS URLs, and stylesheet URLs.
    broken = []
    refs = 0
    for name, dom in pages.items():
        source = ROOT/name
        for node in dom.find():
            urls = [node.attrs[k] for k in ('href','src','poster') if node.attrs.get(k)]
            urls += [x.strip().split()[0] for x in node.attrs.get('srcset','').split(',') if x.strip()]
            urls += re.findall(r'url\([\'\"]?([^\)\'\"]+)', node.attrs.get('style',''))
            for url in urls:
                target = local_target(source,url)
                if target is None:
                    continue
                refs += 1
                path, frag = target
                if not path.is_file():
                    broken.append(f'{name}: {url}')
                elif frag and path.suffix == '.html':
                    target_dom = pages.get(path.name)
                    if target_dom is not None and not target_dom.find(id=frag):
                        broken.append(f'{name}: missing fragment {url}')
    for source in (ROOT/'assets').rglob('*.css'):
        for url in re.findall(r'url\([\'\"]?([^\)\'\"]+)',source.read_text(encoding='utf-8')):
            target=local_target(source,url)
            if target is not None:
                refs += 1
                if not target[0].is_file():
                    broken.append(f'{source.relative_to(ROOT)}: {url}')
    check(not broken, f'broken local links/assets: {broken}')
    home = pages['index.html']
    products = home.find(id='produk')[0]
    cards = products.find('article', **{'class':'sport-card'})
    padel = [c for c in cards if c.find('h3')[0].text() == 'Jersey Padel']
    check(len(padel) == 1 and padel[0].find('a')[0].attrs['href'] == '/'+PILLAR, 'padel card target')
    # Regression checks use the commit before the cluster was introduced.
    baseline = '0bee568'
    def old(name):
        return subprocess.check_output(['git','show',f'{baseline}:{name}'],cwd=ROOT).decode('utf-8')
    old_home = old('index.html')
    expected_home, n = re.subn(
        r'(<article class="card sport-card">(?:(?!</article>).)*?<h3>Jersey Padel</h3>(?:(?!</article>).)*?<a class="btn-outline" href=")jasa-pembuatan-jersey-bandung.html(")',
        r'\1/jersey-padel-custom.html\2',old_home,flags=re.S)
    check(n == 1 and expected_home == (ROOT/'index.html').read_text(encoding='utf-8'), 'homepage changed outside padel card')
    for name in ['robots.txt','vercel.json','assets/css/style.css','assets/js/main.js']:
        check(old(name).replace('\r\n','\n') == (ROOT/name).read_text(encoding='utf-8'), f'protected file changed: {name}')
    for name in LEGACY:
        before, after = parse(old(name)), pages[name]
        check(before.find('head')[0].text() == after.find('head')[0].text(), f'{name}: head text changed')
        check(before.find('link',rel='canonical')[0].attrs == after.find('link',rel='canonical')[0].attrs, f'{name}: canonical changed')
        # Only a single contextual paragraph is permitted as the legacy delta.
        current = (ROOT/name).read_text(encoding='utf-8')
        addition = re.findall(r'<p>(?:(?!</p>).)*?<a href="/jersey-padel-custom.html">(?:(?!</p>).)*?</p>',current,flags=re.S)
        check(len(addition)==1 and current.replace(addition[0],'') == old(name).replace('\r\n','\n'), f'{name}: unexpected legacy changes')
    shell = parse(old('bahan-jersey-full-printing.html'))
    for name in NEW:
        for tag in ['header', 'footer']:
            check(pages[name].find(tag)[0].text() == shell.find(tag)[0].text(), f'{name}: shared {tag} content changed')
    locs=[x.text for x in ET.parse(ROOT/'sitemap.xml').findall('.//{*}loc')]
    before_locs=[x.text for x in ET.fromstring(old('sitemap.xml')).findall('.//{*}loc')]
    check(len(locs)==len(set(locs)), 'sitemap duplicates')
    check(set(locs)-set(before_locs) == {BASE+n for n in NEW}, 'sitemap additions differ from 11 new URLs')
    check(set(before_locs).issubset(locs), 'old sitemap URL removed')
    for url in locs:
        check(url.startswith(BASE), f'sitemap domain: {url}')
    # Similarity: visible article body only; exclude global navigation/footer/sidebar.
    duplicate_paragraphs=[]
    paragraphs=defaultdict(list)
    for name in NEW:
        article=pages[name].find('article',**{'class':'article'})[0]
        for p in article.find('p'):
            normalized=' '.join(words(p.text()))
            if len(words(normalized)) >= 25:
                paragraphs[normalized].append(name)
    duplicate_paragraphs=[names for names in paragraphs.values() if len(set(names))>1]
    check(not duplicate_paragraphs, f'repeated paragraphs: {duplicate_paragraphs}')
    similarities=[]
    for a,b in combinations(NEW,2):
        wa,wb=words(article_texts[a]),words(article_texts[b])
        na={tuple(wa[i:i+5]) for i in range(len(wa)-4)}
        nb={tuple(wb[i:i+5]) for i in range(len(wb)-4)}
        score=len(na&nb)/len(na|nb)
        similarities.append((score,a,b))
    highest=max(similarities)
    check(highest[0] < .08, f'high 5-gram overlap: {highest}')
    http_checks = {}
    if args.http_base:
        base = args.http_base.rstrip('/')+'/'
        check(urlsplit(base).hostname in ('127.0.0.1','localhost','::1'), 'HTTP smoke test is local-only')
        if urlsplit(base).hostname in ('127.0.0.1','localhost','::1'):
            for route in ['']+NEW+['assets/css/style.css','assets/js/main.js','assets/images/product-padel-new.webp','sitemap.xml']:
                try:
                    with urlopen(base+route, timeout=10) as response:
                        status = response.status
                        payload = response.read()
                        http_checks['/'+route] = status
                        check(status == 200 and bool(payload), f'HTTP {status}: {route}')
                        if route in NEW:
                            check(b'charset="utf-8"' in payload, f'HTTP charset: {route}')
                except Exception as exc:
                    check(False,f'HTTP {route}: {exc}')
    print(json.dumps({'new_pages':len(NEW),'all_html_pages':len(pages),'local_references_checked':refs,
        'word_counts_main_article':counts,'meta_description_lengths':meta,'contextual_peer_links':peer_links,
        'highest_pairwise_5gram_jaccard':{'score':round(highest[0],5),'pages':highest[1:]},
        'shared_paragraphs_25_words_or_more':duplicate_paragraphs,
        'sitemap_urls':len(locs),'sitemap_added':len(locs)-len(before_locs),'http_checks':http_checks,
        'errors':errors},ensure_ascii=False,indent=2))
    return bool(errors)

if __name__ == '__main__':
    sys.exit(main())
