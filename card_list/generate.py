import json
import re
import shutil
import requests
from pathlib import Path
from collections import OrderedDict
from typing import List, Dict
from zipfile import ZipFile, ZIP_LZMA
from copy import deepcopy
import tempfile
import numpy as np
import cv2
from tqdm.auto import tqdm
import argparse

# sorting criteria
# level -> code
# special case: upgrade version will follow just after
# investigate & signature inserting at the start

def get_path(cycle: str, working_directory: Path = Path(__file__).parent) -> tuple[Path, Path, Path, Path, Path]:
    """get path from the cwd

    Args:
        cycle (str): name of cycle
        working_directory (Path, optional): working director. Defaults to Path(__file__).parent.

    Raises:
        FileNotFoundError: necessary file not found

    Returns:
        tuple[Path, Path, Path, Path, Path]: folders
    """
    data_folder = working_directory / Path('../../arkhamdb-json-data')
    template_file = working_directory / Path("card_list_template.html")
    output_json = working_directory / Path("outputs.json")
    output_disp = working_directory / Path("dist")
    output_file = working_directory / Path("dist.zip")

    if not template_file.is_file():
        raise FileNotFoundError(template_file)

    if not data_folder.is_dir():
        raise FileNotFoundError(data_folder)

    output_disp.mkdir(exist_ok=True)
    return data_folder, template_file, output_json, output_disp, output_file

def get_data(path_en: Path, path_ko: Path) -> list[dict[str, str]]:
    """generate data structure

    Args:
        path_en (Path): path for english aklcg db
        path_ko (Path): path for korean aklcg db

    Raises:
        ValueError: code keys are not same

    Returns:
        list[dict[str, str]]: data structure
    """
    packs = [
        x.name for x in path_en.iterdir()
        if x.suffix == '.json' and \
        x.name != x.parent.name + "c.json" and \
        x.name.find('encounter') == -1
    ]
    data: list[dict[str, str]] = []
    for pack in packs:
        path = path_en / pack
        with open(path, 'r', encoding='utf-8') as fileio:
            data_eng: list[dict[str, str]] = json.load(fileio)
        path = path_ko / pack
        with open(path, 'r', encoding='utf-8') as fileio:
            data_kor: list[dict[str, str]] = json.load(fileio)
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
    return data

def sort_data(data: list[dict[str, str]]) -> list[dict[str, str]]:
    """sort data structure
    1. investigator and its signature cards
    2. faction-base sorting
    3. upgrade card follows just after the low-level card

    Args:
        data (list[dict[str, str]]): data structure

    Returns:
        list[dict[str, str]]: sorted data structure
    """
    data = deepcopy(data)
    code = [x['code'] for x in data]
    data.sort(key=lambda x: x['code'])
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
    return data

def save_json(data: list[dict[str, str]], path: Path):
    """save json path

    Args:
        data (list[dict[str, str]]): data structure
        path (Path): path to save (.json)
    """
    string = json.dumps(data, ensure_ascii=False, indent=4)
    with open(path, 'w', encoding='utf-8') as fileio:
        fileio.write(string)

def save_html(data: list[dict[str, str]], template: Path, path: Path):
    """save html path

    Args:
        data (list[dict[str, str]]): data structure
        template (Path): path of template html
        path (Path): path of save (directory)
    """
    string = json.dumps(data, ensure_ascii=False, indent=4)

    with open(template, 'r', encoding='utf-8') as fileio:
        html_string = fileio.read()

    html_string = html_string.replace(
        "var printData = []",
        "var printData = "+string
    )
    with open(path / "card_list.html", 'w', encoding='utf-8') as fileio:
        fileio.write(html_string)
        
    path_root = Path(__file__).parent.parent
    for name in ["js", "css", "fonts"]:
        shutil.copytree(path_root / name, path / name, dirs_exist_ok=True)
        shutil.copytree(path_root / name, path / name, dirs_exist_ok=True)
        shutil.copytree(path_root / name, path / name, dirs_exist_ok=True)

def download_cards(data: list[dict[str, str]], save_path: Path):
    """download cards from ArkhamDB website
    NOTE: please use carefully to avoid harsh traffic of webpage

    Args:
        data (list[dict[str, str]]): data structure
        save_path (Path): card download path
    """
    temp_folder = tempfile.TemporaryDirectory()
    for card in tqdm(data):
        if "back_flavor" in card or "back_text" in card:
            codes = [card["code"], card["code"]+"b"]
        else:
            codes = [card["code"]]
        
        for code in codes:
            path = save_path / (code + ".jpg")
            if not path.is_file() or path.stat().st_size < 1000:
                url = 'https://arkhamdb.com/bundles/cards/%s.png'%code
                req = requests.get(url)
                if not req.ok:
                    url = 'https://arkhamdb.com/bundles/cards/%s.jpg'%code
                    req = requests.get(url)
                buffer = np.frombuffer(req.content, np.uint8)
                if buffer.size == 0:
                    image = np.zeros((1, 1), dtype=np.uint8)
                else:
                    image = cv2.imdecode(buffer, cv2.IMREAD_UNCHANGED)
                    image = cv2.resize(image, (300, 418) if image.shape[0]>image.shape[1] else (418, 300))
                temp_path = temp_folder.name + f"/{code}.jpg"
                res = cv2.imwrite(temp_path, image)
                assert res, f"write fail: {path}"
                shutil.move(temp_path, path)
    temp_folder.cleanup()

def arg_parse():
    parser = argparse.ArgumentParser(
        prog="card_list_generator",
        description="generate card list for AHLCG from DB"
    )
    parser.add_argument('cycle', default='fhv', type=str, nargs='?', help='name of cycle')
    parser.add_argument('-d', '--download', action='store_true', default=False, help='true if cards should be downloaded')
    parser.add_argument('--path', default=None, type=str, help='work directory (do not change if you do not know)')
    return parser.parse_args()

def main():
    args = arg_parse()
    wd = args.path
    cycle = args.cycle
    download_card = args.download

    data_folder, template_file, output_json, output_disp, output_file = get_path(wd)

    json_folder_en = data_folder / 'pack' / cycle
    json_folder_ko = data_folder / 'translations/ko/pack' / cycle
    
    data = get_data(json_folder_en, json_folder_ko)
    data = sort_data(data)

    if output_json is not None:
        save_json(data, output_json)
    save_html(data, template_file, output_disp)

    output_card = output_disp / "cards"
    output_card.mkdir(exist_ok=True)

    if download_card is True:
        download_cards(data, output_card)

    if output_file is not None:
        with ZipFile(output_file, "w", ZIP_LZMA) as fileio:
            target = ["css", "fonts", "js", "cards"]
            for input_dir in map(lambda x: output_disp / x, target):
                if not input_dir.is_dir():
                    continue
                for file in input_dir.iterdir():
                    fileio.write(file, input_dir.stem + "/" + file.name)
            fileio.write(output_disp / "card_list.html", "card_list.html")

if __name__ == '__main__':
    main()