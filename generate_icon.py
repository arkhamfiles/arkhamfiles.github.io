import os
import json
import fontforge

def generate_glyph(font: fontforge.font, key: str, name: str, path: str):
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



if __name__ == '__main__':
    generate_fonts()
    generate_css()
