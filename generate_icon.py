#!/usr/bin/env python3
"""generate font file for icon

This script will generate icon font file using svg files.

Requirements:
 * info.json for metadata of icon data
 * default.ttx for metadata of font information

LICENCE:
Please check the README.md of this repo.
This script will be distributed via MIT LICENCE.
However, SVG file and FONT has copyright.

If you need ttx file, you can find free font file and extract via
font = TTFont("path_of_font")
font.saveXML("path_to_save.ttx")
Then, manually modify it
(delete glyf table, modify name table...)

"""

from os import PathLike
import argparse
import json
import re
from pathlib import Path
from collections import Counter
from fontTools.ttLib.ttFont import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc import transform
from fontTools import svgLib
from ftCLI.Lib.Font import Font
from ftCLI.Lib.converters.ttf_to_otf import TrueTypeToCFF
from ftCLI.Lib.converters.otf_to_ttf import CFFToTrueType
from ftCLI.Lib.converters.sfnt_to_web import SFNTToWeb


def generate_ttf(path_info: PathLike, path_xml: PathLike, path_save: PathLike, refine: bool=False):
    """generate truetype font from files

    Args:
        path_info (Path): path of information file
        path_xml (Path): path of xml file for fonttools
        path_save (Path): font save path
        refine (bool, optional): whether refinement performed using ftCLI. Defaults to False.
    """
    path_info = Path(path_info)
    path_xml = Path(path_xml)
    path_save = Path(path_save)

    if not path_info.exists():
        raise FileNotFoundError(path_info)
    if not path_xml.exists():
        raise FileNotFoundError(path_xml)
    if not path_save.parent.is_dir():
        raise FileNotFoundError("parent of save path is directory:", path_save)

    with path_info.open(encoding='utf-8') as file:
        data = json.loads(file.read())

    cnt = Counter()
    for info in data:
        cnt[info['char']] += 1
    if cnt.most_common()[0][1] > 1:
        illegals = [x for x, y in cnt.items() if y > 1]
        raise ValueError("Duplicated Char Mapping in info file:", illegals)
    del cnt

    font = TTFont(sfntVersion="\x00\x01\x00\x00", flavor=False)
    font.importXML(path_xml)

    sample_text = ''
    for info in data:
        name = info['name']
        path = path_info.parent / info['path']
        svg = svgLib.path.SVGPath(path)
        el = svg.root.find("{http://www.w3.org/2000/svg}g")
        if el is not None and el.get('transform', None) is not None:
            tr = el.get('transform', None)
            number = r'([+-]?[0-9]+\.[0-9]+)'
            matchtxt = re.compile(
                r'translate\('+number+r','+number+r'\) scale\('+number+r','+number+r'\)'
            )
            match = matchtxt.match(tr)
            match = tuple(map(float, match.groups()))
            svg.transform = transform.Identity.translate(
                match[0], match[1]
            ).scale(match[2], match[3])
        bpen = BoundsPen(None)
        svg.draw(bpen)
        xMin, yMin, xMax, yMax = bpen.bounds
        scale = min(950/(xMax-xMin), 800/(yMax-yMin))
        dx = 500 - 0.5*scale*(xMin+xMax)
        dy = 500 + 0.5*scale*(yMin+yMax)
        tf = transform.Identity.translate(dx, dy).scale(scale, -scale)
        pen = TTGlyphPen({ord(info['char']): name})
        if svg.transform is None:
            svg.transform = tf
        else:
            svg.transform = tf.transform(svg.transform)
        svg.transform = transform.Identity.translate(0, -200).transform(svg.transform)
        svg.draw(pen)
        glyph = pen.glyph()
        glyph.trim()
        font['glyf'][name] = glyph
        for cmap in font['cmap'].tables:
            cmap.cmap[ord(info['char'])] = name
        sample_text += info['char']
    font['name'].addName(sample_text, ((0, 3, 0x0), (1, 0, 0x0), (3, 1, 0x0409)), 18)

    for name, glyph in font['glyf'].glyphs.items():
        glyph.recalcBounds(font)
        glyph.xMin = max(0, glyph.xMin)
        glyph.yMin = max(0, glyph.yMin)
        glyph.xMax = min(950, glyph.xMax)
        glyph.yMax = min(950, glyph.yMax)
        if name in font['hmtx'].metrics:
            continue
        font['hmtx'][name] = 950, glyph.xMin

    font.setGlyphOrder(font['glyf'].glyphOrder)

    for table in font.tables.values():
        if hasattr(table, 'compile'):
            table.compile(font)

    font.save(path_save)
    if refine:
        font = Font(path_save)
        t2o = TrueTypeToCFF(font)
        t2o.run()
        o2t = CFFToTrueType(t2o.font)
        o2t.run()
        o2t.font.save(path_save)

def convert_others(path_ttf: PathLike, refine: bool=True):
    """generate other fonts from truetype fonts
    - otf, woff, woff2
    at same folder with different suffix.

    Args:
        path_ttf (PathLike): path of truetype font
        refine (bool, optional): whether refinement performed for TTF using ftCLI. Defaults to True.
    """
    path_ttf = Path(path_ttf)
    if path_ttf.suffix != '.ttf':
        raise ValueError("suffix of TTF file should be .ttf")
    if not path_ttf.exists():
        raise FileNotFoundError(path_ttf)
    font = Font(path_ttf)
    ttf2otf = TrueTypeToCFF(font)
    ttf2otf.run()
    ttf2otf.font.save(path_ttf.with_suffix('.otf'))
    if refine:
        otf2ttf = CFFToTrueType(Font(path_ttf.with_suffix('.otf')))
        otf2ttf.run()
        otf2ttf.font.save(path_ttf.with_suffix('.ttf'))
    sfnt2web = SFNTToWeb(Font(path_ttf.with_suffix('.ttf')), 'woff')
    sfnt2web.run()
    sfnt2web.font.save(path_ttf.with_suffix('.woff'))
    sfnt2web = SFNTToWeb(Font(path_ttf.with_suffix('.ttf')), 'woff2')
    sfnt2web.run()
    sfnt2web.font.save(path_ttf.with_suffix('.woff2'))

def generate_css(path_info: PathLike, path_font: PathLike, path_css: PathLike):
    """generate css file for icon font

    Args:
        path_info (PathLike): path of font information json
        path_font (PathLike): path of font (anyone)
        path_css (PathLike): paht of css generation
    """
    path_info = Path(path_info)
    path_font = Path(path_font)
    path_css = Path(path_css)
    if not path_info.exists():
        raise FileNotFoundError(path_info)
    
    with path_info.open(encoding='utf-8') as filept:
        data = json.load(filept)
    font = TTFont(path_font)
    files = []
    for fp in path_font.parent.iterdir():
        if fp.stem == path_font.stem:
            string = str(fp).replace('\\', '/')
            if fp.suffix == '.otf':
                files.append((string, 'opentype'))
            elif fp.suffix == '.ttf':
                files.append((string, 'truetype'))
            else:
                files.append((string, fp.suffix[1:]))
    s = ",\n    ".join(map(lambda x: f"url('../{x[0]}') format('{x[1]}')", files))
    header = f"""@font-face {{
    font-family: '{font['name'].getBestFamilyName()}';
    src: {s};
    font-weight: normal;
    font-style: normal;
}}
[class^="symbol-"],[class*=" symbol-"] {{
    font-family: '{font['name'].getBestFamilyName()}';
    font-style: normal;
    font-weight: normal;
    font-variant: normal;
    text-transform: none;
    line-height: 1;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale
}}"""
    with path_css.open('w', encoding='utf-8') as filept:
        print(header, file=filept)
        print(file=filept)
        for item in data:
            filept.write('.symbol-{name}:before {{\n    content: "{char}"\n}}\n\n'.format(**item))

def main():
    """main function
    TODO: argument parser
    """
    parser = argparse.ArgumentParser(
        description="Autometric font generator for icon files. parser will be updated"
    )
    generate_ttf("svgs/info.json", "svgs/default.ttx", "fonts/arkham-symbols.ttf", True)
    convert_others("fonts/arkham-symbols.ttf", True)
    generate_css("svgs/info.json", "fonts/arkham-symbols.ttf", "css/symbols.css")

if __name__ == '__main__':
    main()
