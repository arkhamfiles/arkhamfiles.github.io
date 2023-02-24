#!/usr/bin/env python3
import os
import json
import logging
import time
from typing import Dict, List
from pathlib import Path
from fontTools import ttLib

def check_update_necessary(base: Path, want: Path) -> bool:
    """check whether update is necessary based on fixed time

    Args:
        base (Path): target based file
        want (Path): generated

    Returns:
        bool: True if update is necessary
    """
    logger = logging.getLogger("check_update")
    if not want.exists():
        logger.debug("target doesn't exist: %s", want)
        return True
    baseinfo = base.stat()
    wantinfo = want.stat()
    logger.debug("basetime: %d, wanttime: %d", baseinfo.st_mtime_ns, wantinfo.st_mtime_ns)
    if baseinfo.st_mtime_ns > wantinfo.st_mtime_ns:
        logger.debug("base is newer; updated")
        return True
    logger.debug("base is older; skip")
    return False

# def generate_glyph(font: fontforge.font, key: str, name: str, path: str) -> fontforge.glyph:
#     glyph = font.createChar(ord(key), name)
#     glyph.importOutlines(path)
#     return glyph

# def generate_fonts():
#     with open('svgs/info.json') as filept:
#         data = json.load(filept)
#     font = fontforge.font()
#     for item in data:
#         glyph = font.createChar(ord(item['char']), item['name'])
#         glyph.importOutlines(os.path.join('svgs', item['path']))
#     font.generate("fonts/arkham-symbols.ttf")
#     font.generate("fonts/arkham-symbols.otf")
#     font.generate("fonts/arkham-symbols.woff")
#     font.generate("fonts/arkham-symbols.svg")

def generate_fonts(path_save: Path):
    extension = path_save.suffix
    sfntVersion = '\x00\x01\x00\x00'
    flavor = None
    if extension == '.ttf':
        pass
    elif extension == '.otf':
        sfntVersion = 'OTTO'
    elif extension == '.woff':
        flavor = 'woff'
    elif extension == '.woff2':
        flavor = 'woff2'
    elif extension == '.svg':
        pass
    else:
        raise NotImplementedError(f"unknown extension: {extension}")
    
    tt = ttLib.TTFont(sfntVersion=sfntVersion, flavor=flavor)
    

def generate_css(path_info: Path, path_font: Path, path_css: Path):
    """generate css file from info

    Args:
        path_info (Path): information file for symbols
        path_font (Path): save path for font (without extension)
        path_css (Path): save path for css
    """
    with path_info.open(encoding='utf-8') as filept:
        data: List[Dict[str, str]] = json.load(filept)
    relative_font = os.path.relpath(path_font, path_css.parent).replace('\\', '/')
    with path_css.open('w', encoding='utf-8') as filept:
        print("@font-face {",
              "    font-family: 'arkhamsymbols';",
              "    src:",
              f"        url('{relative_font + '.otf'}') format('opentype'), ",
              f"        url('{relative_font + '.ttf'}') format('truetype'), ",
              f"        url('{relative_font + '.woff'}') format('woff'), ",
              f"        url('{relative_font + '.svg'}') format('svg');",
              "    font-weight: normal;",
              "    font-style: normal;\n}\n",
             '[class^="symbol-"],[class*=" symbol-"] {',
             "    font-family: 'arkhamsymbols';",
             "    font-style: normal;",
             "    font-weight: normal;",
             "    font-variant: normal;",
             "    text-transform: none;",
             "    line-height: 1;",
             "    -webkit-font-smoothing: antialiased;",
             "    -moz-osx-font-smoothing: grayscale\n}\n",
             sep="\n", file=filept
        )
        for item in data:
            filept.write(f'.symbol-{item["name"]}:before {{\n    content: "{item["char"]}"\n}}\n\n')

def main(path_info: os.PathLike, path_font: os.PathLike, path_css: os.PathLike):
    """main function

    Args:
        path_info (os.PathLike): information file for symbols
        path_font (os.PathLike): save path for font (without extension)
        path_css (os.PathLike): save path for css
    """
    path_info = Path(path_info)
    path_font = Path(path_font).with_suffix('')
    path_css = Path(path_css)
    # is_update = check_update_necessary(path_info, path_font.with_suffix('.ttf'))
    # if not is_update:
    #     print('the font is not generated (no update exists).')
    #     return
    start_time = time.time()
    # generate_fonts()
    generate_css(path_info, path_font, path_css)
    print(f'generate done: {(time.time()-start_time)*1000:.2f}ms')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main("svgs/info.json", "fonts/arkham-symbols", "css/symbols.css")
