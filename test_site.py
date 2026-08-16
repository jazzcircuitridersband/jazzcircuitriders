#!/usr/bin/env python3
"""
Regression tests for jazzcircuitriders.com

    python3 test_site.py

Every check here exists because something actually broke. Counting things
turned out to be useless - counts stayed right while meaning went wrong -
so these assert relationships instead: does this element have a rule, does
this path point at a real file, does this link resolve.

Exit code 0 = safe to deploy.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(ROOT, 'index.html')

fails, warns = [], []
def fail(t, m): fails.append(f"{t}: {m}")
def warn(t, m): warns.append(f"{t}: {m}")

html = open(HTML, encoding='utf-8').read()
css  = ''.join(re.findall(r'<style>(.*?)</style>', html, re.S))
js   = ''.join(re.findall(r'<script>(.*?)</script>', html, re.S))
body = re.sub(r'<script>.*?</script>', '', re.sub(r'<style>.*?</style>', '', html, flags=re.S), flags=re.S)
body_no_comments = re.sub(r'<!--.*?-->', '', body, flags=re.S)


# ---------------------------------------------------------------- structure
def test_structure():
    if not html.lstrip().lower().startswith('<!doctype html'):
        fail('structure', 'missing DOCTYPE')
    if not html.rstrip().endswith('</html>'):
        fail('structure', 'file does not end with </html>')

    # Paired tags. A greedy regex edit once ate an entire member block and
    # this is what caught it.
    for tag in ['html','head','body','main','header','footer','section','div',
                'p','a','span','ul','ol','li','details','summary','h1','h2',
                'style','script','button']:
        o = len(re.findall(r'<%s[\s>]' % tag, html))
        c = len(re.findall(r'</%s>' % tag, html))
        if o != c:
            fail('structure', f'<{tag}> unbalanced: {o} open, {c} close')

    if css.count('{') != css.count('}'):
        fail('structure', f"CSS braces unbalanced: {css.count('{')}/{css.count('}')}")
    if len(re.findall(r'<h1', html)) != 1:
        fail('structure', f'expected exactly one <h1>, found {len(re.findall(r"<h1", html))}')
    for landmark in ['<main>', '<header', '<footer']:
        if landmark not in html:
            fail('structure', f'missing landmark {landmark}')


# ------------------------------------------------------------ build safety
def test_jekyll_safe():
    """GitHub Pages runs Jekyll. Liquid delimiters fail the build and the
    site 404s with no obvious cause."""
    for token in ['{{', '{%', '}}', '%}']:
        if token in html:
            fail('jekyll', f'{token} present - this will fail the Pages build')
    if html.lstrip().startswith('---'):
        fail('jekyll', 'file starts with --- and will be read as front matter')


# ------------------------------------------------------------------ assets
def test_assets_exist():
    """Every local reference must point at a file that is actually here.
    A hero once pointed at an image that had never existed."""
    refs = set(re.findall(r'(?:src|href)="((?!https?:|mailto:|tel:|#|data:)[^"]+)"', body_no_comments))
    refs |= set(re.findall(r'url\("((?!data:)[^"]+)"\)', css))
    for r in sorted(refs):
        if '..' in r:
            fail('assets', f'{r} uses ../ - breaks when served from a subfolder')
        p = os.path.join(ROOT, r.lstrip('/'))
        if not os.path.exists(p):
            # if the containing folder isn't here either, we're running outside
            # a full checkout - that's a warning, not a broken site
            if os.path.isdir(os.path.dirname(p)):
                fail('assets', f'{r} referenced but not found')
            else:
                warn('assets', f'{r} not present locally (folder absent - run in a full checkout)')


# ------------------------------------------------------------------ images
def test_images():
    for tag in re.findall(r'<img\b[^>]*>', body):
        src = re.search(r'src="([^"]*)"', tag)
        src = src.group(1) if src else '(no src)'
        if not re.search(r'alt="[^"]+"', tag):
            fail('images', f'{src} has no alt text')
        if not (re.search(r'width="\d+"', tag) and re.search(r'height="\d+"', tag)):
            warn('images', f'{src} has no width/height - causes layout shift')


# ------------------------------------------------------------------- links
def test_links():
    """Two failures live here. Links that open new tabs without rel=noopener,
    and links with no CSS rule at all - which is how three of them ended up
    rendering in browser-default blue on a navy background."""
    selectors = [s.strip() for s in re.findall(r'([^{}]+)\{', css)]
    # rules that could style a link: either they target <a> inside something,
    # or they target a class the <a> itself carries
    link_rules = [s for s in selectors
                  if re.search(r'(^|[\s>.#\])])a(\s*[:,{]|$)', s) or '.' in s]

    for tag in re.findall(r'<a\b[^>]*>', body_no_comments):
        rel = re.search(r'rel="([^"]*)"', tag)
        rel_tokens = rel.group(1).split() if rel else []
        if 'target="_blank"' in tag and 'noopener' not in rel_tokens:
            fail('links', f'new-tab link without rel=noopener: {tag[:70]}')

    # walk the DOM crudely: track open class'd elements to know each link's ancestry
    stack, bare = [], []
    for m in re.finditer(r'<(/?)(\w+)([^>]*)>', body_no_comments):
        closing, tag, attrs = m.group(1), m.group(2), m.group(3)
        if tag == 'a' and not closing:
            cls = re.search(r'class="([^"]*)"', attrs)
            own = cls.group(1).split() if cls else []
            ancestry = own + [c for _, cs in stack for c in cs]
            if not any(('.'+c) in s for s in link_rules for c in ancestry):
                bare.append(attrs.strip()[:60])
        elif tag in ('div','p','section','footer','header','main','span','details','li') and not closing and '/>' not in m.group(0):
            cls = re.search(r'class="([^"]*)"', attrs)
            stack.append((tag, cls.group(1).split() if cls else []))
        elif closing and stack and stack[-1][0] == tag:
            stack.pop()
    for b in bare:
        fail('links', f'no CSS rule covers this link: {b}')


# ------------------------------------------------------- css / html coherence
def test_css_html_coherence():
    """Catches both directions of drift: an element with no rule (the expand
    marker vanished this way) and a rule with no element (dead CSS)."""
    used = set()
    for c in re.findall(r'class="([^"]*)"', body):
        used |= set(c.split())
    # a selector is exactly the text before each "{" - no cleverness needed
    defined = set()
    for sel in re.findall(r'([^{}]+)\{', css):
        defined |= set(re.findall(r'\.([a-zA-Z][\w-]*)', sel))
    # classes the JavaScript applies at runtime are legitimately absent from HTML
    used |= set(re.findall(r"classList\.(?:add|remove|toggle|contains)\('([\w-]+)'", js))
    for s in re.findall(r'class=\\?"([\w\- ]+)', js):
        used |= set(s.split())

    for c in sorted(used - defined):
        warn('css', f'.{c} used in HTML but has no rule')
    for c in sorted(defined - used):
        warn('css', f'.{c} defined in CSS but never used')


# ----------------------------------------------------------- accessibility
def test_accessibility():
    if 'lang="' not in html:
        fail('a11y', 'no lang attribute on <html>')
    if 'class="skip"' not in html:
        fail('a11y', 'skip link missing')
    if 'prefers-reduced-motion' not in css:
        fail('a11y', 'no reduced-motion handling')
    if ':focus-visible' not in css:
        fail('a11y', 'no visible focus styles')
    for sec in re.findall(r'<section[^>]*>', body):
        if 'aria-labelledby' not in sec:
            fail('a11y', f'section without accessible name: {sec[:60]}')
    for btn in re.findall(r'<button\b[^>]*>', body):
        if 'aria-label' not in btn:
            fail('a11y', f'button without label: {btn[:60]}')
    for inp in re.findall(r'<input\b[^>]*>', body):
        if 'aria-label' not in inp:
            fail('a11y', f'input without label: {inp[:60]}')
    # expand markers must only appear on rows that expand
    for sel in re.findall(r'([^{}]*::after)\s*\{[^}]*content:"[+\\]', css):
        if 'details' not in sel:
            fail('a11y', f'expand marker not scoped to <details>: {sel.strip()}')


# --------------------------------------------------------------- contrast
def _lum(hexstr):
    h = hexstr.lstrip('#')
    c = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    c = [x/12.92 if x <= 0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return .2126*c[0] + .7152*c[1] + .0722*c[2]

def _ratio(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi+.05)/(lo+.05)

def test_contrast():
    """Text colours against the page background, WCAG AA (4.5:1)."""
    tokens = dict(re.findall(r'--([\w-]+):\s*(#[0-9A-Fa-f]{6})', css))
    bg = tokens.get('ink')
    if not bg:
        fail('contrast', 'could not find --ink background token')
        return
    for name in ['cream', 'steel', 'brass', 'brass-lit']:
        if name in tokens:
            r = _ratio(tokens[name], bg)
            if r < 4.5:
                fail('contrast', f'--{name} {tokens[name]} is {r:.2f}:1 on {bg}, needs 4.5:1')


# ------------------------------------------------------- content hygiene
def test_no_placeholders():
    """Placeholder copy that sounds plausible is the dangerous kind. 'Est. on
    the road' survived weeks of review because it read like real writing."""
    for pat in ['Track One Title', 'Track Two Title', 'Track Three Title',
                'Venue Name', 'Band Name', 'Lorem ipsum', '555-0123',
                '______', 'REPLACE_ME', 'TODO', 'FIXME']:
        if pat in body_no_comments:
            fail('content', f'placeholder still visible on the page: "{pat}"')
    if 'REPLACE' in body and 'REPLACE' not in re.sub(r'<!--.*?-->', '', body, flags=re.S):
        pass  # REPLACE inside comments is fine - it's a note to ourselves


# -------------------------------------------------------------------- seo
def test_seo():
    t = re.search(r'<title>(.*?)</title>', html)
    if not t:
        fail('seo', 'no <title>')
    elif len(t.group(1)) > 60:
        warn('seo', f'title is {len(t.group(1))} chars, Google truncates near 60')
    d = re.search(r'<meta name="description" content="([^"]*)"', html)
    if not d:
        fail('seo', 'no meta description')
    elif len(d.group(1)) > 160:
        warn('seo', f'description is {len(d.group(1))} chars, truncates near 155')
    for need in ['rel="canonical"', 'og:title', 'og:description', 'og:image', 'og:url']:
        if need not in html:
            fail('seo', f'missing {need}')
    ld = re.search(r'application/ld\+json">(.*?)</script>', html, re.S)
    if not ld:
        fail('seo', 'no JSON-LD structured data')
    else:
        try:
            data = json.loads(ld.group(1))
            for k in ['name', 'url', 'address', 'areaServed']:
                if k not in data:
                    fail('seo', f'structured data missing "{k}"')
        except Exception as e:
            fail('seo', f'JSON-LD does not parse: {e}')

    # og:url and canonical should agree, and point where the site actually is
    can = re.search(r'rel="canonical" href="([^"]*)"', html)
    og  = re.search(r'og:url" content="([^"]*)"', html)
    if can and og and can.group(1) != og.group(1):
        fail('seo', 'canonical and og:url disagree')


# ------------------------------------------------------------------ shows
def test_shows_json():
    p = os.path.join(ROOT, 'shows.json')
    if not os.path.exists(p):
        fail('shows', 'shows.json missing - the site will fall back to sample dates')
        return
    try:
        data = json.load(open(p))
    except Exception as e:
        fail('shows', f'shows.json does not parse ({e}) - live site will show BACKUP dates')
        return
    if not isinstance(data, list):
        fail('shows', 'shows.json must be a list')
        return
    for i, s in enumerate(data):
        # say what the entry actually IS - "missing date" on a string is useless
        if not isinstance(s, dict):
            fail('shows', f'entry {i} is a {type(s).__name__}, not an object: {str(s)[:60]!r}')
            continue
        missing = [k for k in ('date', 'venue', 'city') if k not in s]
        if missing:
            fail('shows', f'entry {i} missing {missing} — it has {sorted(s.keys())}')
        if 'date' in s and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(s['date'])):
            fail('shows', f'entry {i} date "{s["date"]}" is not YYYY-MM-DD')


# ------------------------------------------------------------------ audio
def test_audio_players():
    """Assert the shape of each track rather than counting them."""
    for li in re.findall(r'<li class="track"[^>]*>.*?</li>', body, re.S):
        src = re.search(r'data-src="([^"]+)"', li)
        if not src:
            fail('audio', 'track with no data-src')
            continue
        name = src.group(1)
        if not re.search(r'<button[^>]*aria-label="[^"]+"', li):
            fail('audio', f'{name}: play button has no label')
        if not re.search(r'<input[^>]*type="range"[^>]*aria-label="[^"]+"', li):
            fail('audio', f'{name}: scrub bar is not a labelled range input')
        if not re.search(r'class="track-title">[^<]+<', li):
            fail('audio', f'{name}: no visible title')



# ------------------------------------------------------- unreferenced files
def test_no_orphan_files():
    """Files sitting in the repo that nothing points at. Runs against the real
    checkout in CI, which is the only listing that counts."""
    # needed but never linked from a page
    expected = {
        'index.html', 'shows.json', 'README.md', 'test_site.py',
        'CNAME', 'robots.txt', 'sitemap.xml',
        'favicon.svg', 'favicon.ico', 'apple-touch-icon.png',
        '.gitignore', '.nojekyll', '404.html', 'manifest.webmanifest',
    }
    body = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    refs = set(re.findall(r'(?:src|href)="((?!https?:|mailto:|tel:|#|data:)[^"]+)"', body))
    refs |= set(re.findall(r'url\("((?!data:)[^"]+)"\)', body))
    refs |= set(re.findall(r"fetch\('([^']+)'", body))
    refs = {r.lstrip('./') for r in refs}

    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in ('.git', '.github', '__pycache__')]
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT).replace(os.sep, '/')
            if rel in expected or rel in refs:
                continue
            if fn == '.gitkeep':
                warn('orphans', f'{rel} — placeholder, folder has real files now')
            else:
                warn('orphans', f'{rel} — in the repo but nothing references it')


# ------------------------------------------------- image dimension accuracy
def _img_size(path):
    """Read width/height from PNG or WebP headers. No dependencies."""
    with open(path, 'rb') as f:
        head = f.read(40)
    if head[:8] == b'\x89PNG\r\n\x1a\n':
        return int.from_bytes(head[16:20],'big'), int.from_bytes(head[20:24],'big')
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        fmt = head[12:16]
        if fmt == b'VP8 ':
            return int.from_bytes(head[26:28],'little') & 0x3fff, int.from_bytes(head[28:30],'little') & 0x3fff
        if fmt == b'VP8L':
            b = int.from_bytes(head[21:25],'little')
            return (b & 0x3fff)+1, ((b >> 14) & 0x3fff)+1
        if fmt == b'VP8X':
            return (int.from_bytes(head[24:27],'little'))+1, (int.from_bytes(head[27:30],'little'))+1
    return None

def test_image_dimensions():
    """An image reused somewhere bigger than it was made for goes soft, and
    nothing errors. Declared width/height must match the real file."""
    for tag in re.findall(r'<img\b[^>]*>', body):
        src = re.search(r'src="([^"]+)"', tag)
        w   = re.search(r'width="(\d+)"', tag)
        hh  = re.search(r'height="(\d+)"', tag)
        if not (src and w and hh):
            continue
        p = os.path.join(ROOT, src.group(1))
        if not os.path.exists(p):
            continue
        real = _img_size(p)
        if not real:
            warn('images', f'{src.group(1)} — could not read dimensions')
            continue
        if (real[0], real[1]) != (int(w.group(1)), int(hh.group(1))):
            fail('images', f'{src.group(1)} is {real[0]}x{real[1]} '
                           f'but declared {w.group(1)}x{hh.group(1)}')


# --------------------------------------------------- performance regressions
def test_audio_not_eager():
    """Creating Audio objects at page load once pulled 22MB of MP3 before
    anyone pressed play. LCP went to 52 seconds. Never again."""
    m = re.search(r'tracks\.forEach\(function \(track\) \{(.*?)\n  \}\);', js, re.S)
    if not m:
        warn('perf', 'could not locate the track loop to check audio loading')
        return
    loop = m.group(1)
    # every `new Audio(` must sit inside a function that runs on interaction
    for hit in re.finditer(r'new Audio\(', loop):
        before = loop[:hit.start()]
        if 'function build' not in before:
            fail('perf', 'Audio object created outside a click handler — '
                         'this fetches every MP3 on page load')
    if re.search(r"preload\s*=\s*['\"]metadata['\"]", loop) and 'function build' not in loop:
        fail('perf', "preload='metadata' at page load fetches all audio")

def test_no_opacity_on_text():
    """Colour tokens can pass contrast and still fail once opacity composites
    them against the background. Lighthouse caught one I missed."""
    for m in re.finditer(r'(\.[\w-]+)\{([^}]*)\}', css):
        name, decl = m.group(1), m.group(2)
        if re.search(r'opacity:\s*0?\.[0-8]', decl) and 'font-size' in decl:
            warn('contrast', f'{name} sets opacity on text — check the composited ratio')


# ------------------------------------------------------- invalid HTML nesting
def test_no_invalid_nesting():
    """A <p> cannot contain a block element. Browsers silently close the <p>
    first, which quietly restructures the DOM and breaks styling that assumed
    the original shape."""
    for m in re.finditer(r'<p\b[^>]*>(.*?)</p>', body, re.S):
        for bad in ('<div', '<h1', '<h2', '<h3', '<h4', '<ul', '<ol', '<section', '<p '):
            if bad in m.group(1):
                fail('html', f'{bad}> inside a <p> — invalid, browsers will reparse it')

if __name__ == '__main__':
    for fn in [test_structure, test_jekyll_safe, test_assets_exist, test_images,
               test_links, test_css_html_coherence, test_accessibility,
               test_contrast, test_no_placeholders, test_seo,
               test_shows_json, test_audio_players, test_no_orphan_files, test_image_dimensions, test_audio_not_eager, test_no_opacity_on_text, test_no_invalid_nesting]:
        fn()

    for w in warns:
        print(f"  WARN  {w}")
    for f in fails:
        print(f"  FAIL  {f}")
    print()
    if fails:
        print(f"{len(fails)} failure(s), {len(warns)} warning(s) - do not deploy")
        sys.exit(1)
    print(f"All checks passed ({len(warns)} warning(s)) - safe to deploy")
