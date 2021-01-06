import os
import json
import logging
import time
import fontforge

def check_update_necessary(base: str, want: str) -> bool:
    """check whether update is necessary based on fixed time

    Args:
        base (str): target based file
        want (str): generated

    Returns:
        bool: True if update is necessary
    """
    logger = logging.getLogger("check_update")
    if not os.path.isfile(want):
        logger.debug("target doesn't exist: %s", want)
        return True
    baseinfo = os.stat(base)
    wantinfo = os.stat(want)
    logger.debug("basetime: %d, wanttime: %d", baseinfo.st_mtime_ns, wantinfo.st_mtime_ns)
    if baseinfo.st_mtime_ns > wantinfo.st_mtime_ns:
        logger.debug("base is newer; updated")
        return True
    logger.debug("base is older; skip")
    return False

def generate_glyph(font: fontforge.font, key: str, name: str, path: str) -> fontforge.glyph:
    glyph = font.createChar(ord(key), name)
    glyph.importOutlines(path)
    return glyph

def generate_fonts():
    with open('svgs/info.json') as filept:
        data = json.load(filept)
    font = fontforge.font()
    for item in data:
        glyph = font.createChar(ord(item['char']), item['name'])
        glyph.importOutlines(os.path.join('svgs', item['path']))
    font.generate("fonts/arkham-symbols.ttf")
    font.generate("fonts/arkham-symbols.otf")
    font.generate("fonts/arkham-symbols.woff")
    font.generate("fonts/arkham-symbols.svg")

def generate_css():
    with open('svgs/info.json') as filept:
        data = json.load(filept)
    header = """@font-face {
    font-family: 'arkhamsymbols';
    src: url('../fonts/arkham-symbols.otf');
    src: url('../fonts/arkham-symbols.otf') format('opentype'), 
    url('../fonts/arkham-symbols.ttf') format('truetype'), 
    url('../fonts/arkham-symbols.woff') format('woff'), 
    url('../fonts/arkham-symbols.svg') format('svg');
    font-weight: normal;
    font-style: normal;
}

[class^="symbol-"],[class*=" symbol-"] {
    font-family: 'arkhamsymbols';
    speak: none;
    font-style: normal;
    font-weight: normal;
    font-variant: normal;
    text-transform: none;
    line-height: 1;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale
}"""
    with open("css/symbols.css", 'w', encoding='utf-8') as filept:
        print(header, file=filept)
        print(file=filept)
        for item in data:
            filept.write('.symbol-{name}:before {{\n    content: "{char}"\n}}\n\n'.format(**item))

def main():
    is_update = check_update_necessary('svgs/info.json', "fonts/arkham-symbols.ttf")
    if not is_update:
        print('the font is not generated (no update exists).')
        return
    start_time = time.time()
    generate_fonts()
    generate_css()
    print('generate done: %.2fms'%(time.time()-start_time)*1000)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
