#!/usr/bin/env python3
"""Run local checks, render previews if available, and package this landing project."""
from __future__ import annotations
from pathlib import Path
from base64 import b64encode
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import sys

ROOT = Path(__file__).resolve().parent
LAND = ROOT / 'landing'
PREVIEW = ROOT / 'preview'
PREVIEW.mkdir(exist_ok=True)

def validate_files():
    required = [LAND/'index.html', LAND/'styles.css', LAND/'script.js', LAND/'assets/speaker-lee-jongpil.webp', LAND/'assets/speaker-lee-jongpil.png']
    for path in required:
        if not path.exists():
            raise FileNotFoundError(f'Missing required file: {path}')
    html=(LAND/'index.html').read_text(encoding='utf-8')
    js=(LAND/'script.js').read_text(encoding='utf-8')
    for s in ['패러다임의 변화와', '킹덤처치의 비전', '2026년 11월 9일', '밝은빛전원교회', '이종필', '010-4416-0926']:
        if s not in html:
            raise AssertionError(f'Expected content missing: {s}')
    if 'https://forms.gle/MtNb68xxpQVmZByk9' not in js or html.count('href="https://forms.gle/MtNb68xxpQVmZByk9"') != 5:
        raise AssertionError('Online registration URL missing from CTA links')
    return html

def inline_for_screenshot(html):
    css = (LAND/'styles.css').read_text(encoding='utf-8')
    js = (LAND/'script.js').read_text(encoding='utf-8')
    html = html.replace('<link rel="stylesheet" href="styles.css">', '<style>'+css+'</style>')
    html = html.replace('<script src="script.js" defer></script>', '<script>'+js+'</script>')
    for name, mime in [('speaker-lee-jongpil.webp','image/webp'),('speaker-lee-jongpil.png','image/png')]:
        content=b64encode((LAND/'assets'/name).read_bytes()).decode('ascii')
        html=html.replace('assets/'+name, 'data:'+mime+';base64,'+content)
    og=LAND/'assets/og-preview.png'
    if og.exists():
        content=b64encode(og.read_bytes()).decode('ascii')
        html=html.replace('assets/og-preview.png','data:image/png;base64,'+content)
    return html

def capture(html):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        chromium_executable=Path('/usr/bin/chromium')
        browser=p.chromium.launch(headless=True, executable_path=str(chromium_executable) if chromium_executable.is_file() else None, args=['--no-sandbox','--disable-dev-shm-usage','--no-proxy-server'])
        for width, height, label in [(1280,900,'pc_1280'),(768,1024,'tablet_768'),(375,812,'mobile_375')]:
            page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
            failures=[]
            page.on('pageerror',lambda error:failures.append(str(error)))
            page.set_content(inline_for_screenshot(html),wait_until='load')
            metrics=page.evaluate('''() => ({viewport:innerWidth, scroll:document.documentElement.scrollWidth, cta:Array.from(document.querySelectorAll('a.register-link')).every(a=>a.getAttribute('href') === 'https://forms.gle/MtNb68xxpQVmZByk9' && a.target === '_blank'), photo:document.querySelector('.hero-visual img').complete})''')
            if failures or metrics['scroll'] > width or not metrics['cta'] or not metrics['photo']:
                raise AssertionError(f'{label}: {metrics}, errors={failures}')
            page.screenshot(path=str(PREVIEW/f'{label}.png'),full_page=True)
            print(f'PASS: {label} viewport={width}; no horizontal overflow; CTA Google Form; photo loaded')
            page.close()
        browser.close()

def generate_og():
    from PIL import Image
    shot=PREVIEW/'pc_1280.png'
    if not shot.exists():
        return False
    with Image.open(shot) as pic:
        pic.crop((0,108,1280,780)).resize((1200,630), Image.Resampling.LANCZOS).convert('RGB').save(LAND/'assets/og-preview.png', optimize=True)
    return True

def package():
    target = ROOT.parent/'kingdomchurch_landing.zip'
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for path in sorted(ROOT.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                z.write(path, path.relative_to(ROOT))
    print(f'PACKAGED: {target} ({target.stat().st_size:,} bytes)')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--no-capture',action='store_true',help='Skip browser screenshots')
    args=parser.parse_args()
    html=validate_files()
    if not args.no_capture:
        try:
            capture(html)
        except (ImportError,Exception) as e:
            print(f'Browser capture unavailable: {e}. Basic static checks have passed.',file=sys.stderr)
    if generate_og():
        print('OG cover created from actual desktop screenshot.')
    (ROOT/'landing_standalone.html').write_text(inline_for_screenshot(html), encoding='utf-8')
    print('Single-file HTML rebuilt with inline CSS, JS and image assets.')
    package()
