import json
import re
import shutil
import requests
from pathlib import Path
from collections import OrderedDict
from typing import List, Dict

# sorting criteria
# level -> code
# special case: upgrade version will follow just after
# investigate & signature inserting at the start

cycle = 'tic'
data_folder = Path('../../arkhamdb-json-data')
template_file = Path("card_list_template.html")
output_json = Path("outputs.json")
output_disp = Path("dist")

if not template_file.is_file():
    raise FileNotFoundError(template_file)

if not data_folder.is_dir():
    raise FileNotFoundError(data_folder)

output_disp.mkdir(exist_ok=True)

json_folder_en = data_folder / 'pack' / cycle
json_folder_ko = data_folder / 'translations/ko/pack' / cycle

packs = [
    x.name for x in json_folder_en.iterdir()
    if x.suffix == '.json' and \
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

## one more sort based on code
data.sort(key=lambda x: x['code'])
code = [x['code'] for x in data]

results = []

to_remove = []
invs = [x for x in data if "type_code" in x and x['type_code'] =="investigator"]
sigs: List[List[Dict[str, str]]] = []
for inv in invs:
    sig: List[Dict[str, str]] = []
    reqs = inv['deck_requirements']
    idx = code.index(inv['code'])
    to_remove.append(idx)
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
    value.sort(key=lambda x:int(x['code'])+(x['xp']*100000 if 'xp' in x else 600000))
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

string = json.dumps(data, ensure_ascii=False, indent=4)

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

for card in data:
    if "type_code" in card and card["type_code"] == "investigator":
        code = card["code"]+"b"
        path = output_card / (code + ".png")
        if not path.is_file():
            url = 'https://arkhamdb.com/bundles/cards/%s.png'%code
            req = requests.get(url)
            with open(path, 'wb') as fid:
                fid.write(req.content)
    code = card["code"]
    path = output_card / (code + ".png")
    if not path.is_file():
        url = 'https://arkhamdb.com/bundles/cards/%s.png'%code
        req = requests.get(url)
        with open(path, 'wb') as fid:
            fid.write(req.content)
