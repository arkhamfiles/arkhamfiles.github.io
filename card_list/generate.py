import json
import re
import shutil
import requests
from pathlib import Path
from collections import OrderedDict
from typing import List, Dict
from zipfile import ZipFile, ZIP_LZMA
import numpy as np
import cv2
from tqdm.auto import tqdm

# sorting criteria
# level -> code
# special case: upgrade version will follow just after
# investigate & signature inserting at the start

cycle = 'fhv'
data_folder = Path(__file__).parent / Path('../../arkhamdb-json-data')
template_file = Path(__file__).parent / Path("card_list_template.html")
output_json = Path(__file__).parent / Path("outputs.json")
output_disp = Path(__file__).parent / Path("dist")
output_file = Path(__file__).parent / Path("dist.zip")
download_card = True

if not template_file.is_file():
    raise FileNotFoundError(template_file)

if not data_folder.is_dir():
    raise FileNotFoundError(data_folder)

output_disp.mkdir(exist_ok=True)

json_folder_en = data_folder / 'pack' / cycle
json_folder_ko = data_folder / 'translations/ko/pack' / cycle

### for cycle-type
packs = [
    x.name for x in json_folder_en.iterdir()
    if x.suffix == '.json' and \
    x.name != x.parent.name + "c.json" and \
    x.name.find('encounter') == -1
]
print('PACK:', packs)

data: List[Dict[str, str]] = []

for pack in packs:
    path = json_folder_en / pack
    with open(path, 'r', encoding='utf-8') as fileio:
        data_eng: List[Dict[str, str]] = json.load(fileio)
    path = json_folder_ko / pack
    with open(path, 'r', encoding='utf-8') as fileio:
        data_kor: List[Dict[str, str]] = json.load(fileio)
    data_eng.sort(key=lambda x: x['code'])
    data_kor.sort(key=lambda x: x['code'])
    for e, k in zip(data_eng, data_kor):
        if e['code'] != k['code']:
            raise ValueError(f"{e['code']}, {k['code']} not same?")
        for key, value in k.items():
            e[key] = value
    data.extend(data_eng)
    for item in data:
        if "customization_text" in item:
            item["text"] +=  '\n' + item["customization_text"]

## one more sort based on code
data.sort(key=lambda x: x['code'])
code = [x['code'] for x in data]

results = []

to_remove = []
invs = [x for x in data if "type_code" in x and x['type_code'] == "investigator"]
sigs: List[List[Dict[str, str]]] = []
for inv in invs:
    sig: List[Dict[str, str]] = []
    idx = code.index(inv['code'])
    to_remove.append(idx)
    if 'deck_requirements' in inv:
        reqs = inv['deck_requirements']
        for match in re.finditer(r"card:([0-9]+)", reqs):
            c = match.group(1)
            idx = code.index(c)
            sig.append(data[idx])
            to_remove.append(idx)
    sigs.append(sig)
to_remove.sort()
for idx in reversed(to_remove):
    del data[idx]
    del code[idx]
   
## faction based distribution
cards: Dict[str, List[Dict[str, str]]] = OrderedDict({
    'guardian': [], 'seeker': [], 'mystic': [],
    'rogue': [], 'survivor': [], 'neutral': []
})

for card in data:
    cards[card['faction_code']].append(card)

## sorting based on faction
for key, value in cards.items():
    value.sort(key=lambda x: int(x['code'][:5])+(int(x['xp'])*100000 if 'xp' in x else 600000))
    names = [x['name'] for x in value]
    for i in range(len(value)):
        name = value[i]['name']
        try:
            index = names[i+1:].index(name) + i + 1
        except ValueError:
            continue
        v = value.pop(index)
        value.insert(i+1, v)
        v = names.pop(index)
        names.insert(i+1, v)
    
## inserting investigator to finish
for inv, sig in zip(invs, sigs):
    faction = inv['faction_code']
    for card in reversed(sig):
        cards[faction].insert(0, card)
    cards[faction].insert(0, inv)

data: List[Dict[str, str]] = []
for value in cards.values():
    data.extend(value)
data.sort(key=lambda x: x['code']) # temporary code based sorting

string = json.dumps(data, ensure_ascii=False, indent=4)

if output_json is not None:
    with open(output_json, 'w', encoding='utf-8') as fileio:
        fileio.write(string)

with open(template_file, 'r', encoding='utf-8') as fileio:
    html_string = fileio.read()

html_string = html_string.replace(
    "var printData = []",
    "var printData = "+string
)


with open(output_disp / "card_list.html", 'w', encoding='utf-8') as fileio:
    fileio.write(html_string)

path_root = Path(__file__).parent.parent
for name in ["js", "css", "fonts"]:
    shutil.copytree(path_root / name, output_disp / name, dirs_exist_ok=True)
    shutil.copytree(path_root / name, output_disp / name, dirs_exist_ok=True)
    shutil.copytree(path_root / name, output_disp / name, dirs_exist_ok=True)

output_card = output_disp / "cards"
output_card.mkdir(exist_ok=True)

if download_card is True:
    for card in tqdm(data):
        if "back_flavor" in card or "back_text" in card:
            codes = [card["code"], card["code"]+"b"]
        else:
            codes = [card["code"]]
        
        for code in codes:
            path = output_card / (code + ".jpg")
            if not path.is_file():
                url = 'https://arkhamdb.com/bundles/cards/%s.png'%code
                req = requests.get(url)
                buffer = np.frombuffer(req.content, np.uint8)
                if buffer.size == 0:
                    image = np.zeros((1, 1), dtype=np.uint8)
                else:
                    image = cv2.imdecode(buffer, cv2.IMREAD_UNCHANGED)
                    image = cv2.resize(image, (300, 418) if image.shape[0]>image.shape[1] else (418, 300))
                cv2.imwrite(str(path), image)

if output_file is not None:
    with ZipFile(output_file, "w", ZIP_LZMA) as fileio:
        target = ["css", "fonts", "js", "cards"]
        for input_dir in map(lambda x: output_disp / x, target):
            if not input_dir.is_dir():
                continue
            for file in input_dir.iterdir():
                fileio.write(file, input_dir.stem + "/" + file.name)
        fileio.write(output_disp / "card_list.html", "card_list.html")
