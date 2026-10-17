from pathlib import Path
from playwright.sync_api import sync_playwright
from base64 import b64encode
root=Path('/mnt/data/kingdomchurch_landing')
land=root/'landing'
s=(land/'index.html').read_text(encoding='utf-8')
css=(land/'styles.css').read_text(encoding='utf-8')
js=(land/'script.js').read_text(encoding='utf-8')
s=s.replace('<link rel="stylesheet" href="styles.css">','<style>'+css+'</style>')
s=s.replace('<script src="script.js" defer></script>', '<script>'+js+'</script>')
for name, mimetype in [('speaker-lee-jongpil.webp','image/webp'),('speaker-lee-jongpil.png','image/png')]:
    data=b64encode((land/'assets'/name).read_bytes()).decode('ascii')
    s=s.replace('assets/'+name,f'data:{mimetype};base64,{data}')
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--no-proxy-server'])
    for width,height,label in [(1280,900,'pc_1280'),(768,1024,'tablet_768'),(375,812,'mobile_375')]:
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        page.set_content(s,wait_until='load',timeout=12000)
        page.screenshot(path=str(root/'preview'/f'{label}.png'),full_page=True,timeout=20000)
        data=page.evaluate('''() => ({title: document.title, windowWidth:innerWidth, scrollWidth:document.documentElement.scrollWidth,
          registerLinks:Array.from(document.querySelectorAll('a.register-link')).map(x=>({label:x.innerText.trim(),url:x.getAttribute('href')})),
          heroTitle:document.querySelector('h1').getBoundingClientRect().toJSON(),
          primaryCTA:document.querySelector('.hero-actions .primary-btn').getBoundingClientRect().toJSON(),
          photo:document.querySelector('.hero-visual img').getBoundingClientRect().toJSON(),
          totalHeight:document.documentElement.scrollHeight})''')
        print(label,data, 'page_errors=',errors,flush=True)
        page.close()
    browser.close()
