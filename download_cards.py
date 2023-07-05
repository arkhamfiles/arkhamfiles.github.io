#!/usr/bin/env python3
"""script for download card images from arkhamDB

Instead of load image for each usage, we download necessary images previously.

Currently, we read following cards:
* randomweak.html
* json files

"""

from typing import Iterable, MutableSet, List, Dict
from os import PathLike
from pathlib import Path
import json
import re
import requests
from tqdm.auto import tqdm
import cv2 # pip install opencv-python

def get_randomweak(path: PathLike) -> MutableSet[str]:
    """get cards data from randomweak html"""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    re_card = re.compile(
        r"{name: '(?:[^']+)', pack: PACK_(?:[A-Z_]+), code: '([^']+)', count: (?:[0-9]+)[^}]*}"
    )
    cards = set()
    with path.open("r", encoding="utf-8") as fid:
        for line in fid:
            match = re_card.search(line)
            if match is None:
                continue
            cards.add(match.group(1)) # code
    return cards

def get_json(path: PathLike) -> MutableSet[str]:
    """get cards data from json"""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as fid:
        data: List[Dict[str, str]] = json.load(fid)
    cards = set(x['code'] for x in data)
    return cards

def download_cards(path: PathLike, cards: Iterable[str]) -> None:
    """download given cards from arkhamdb

    Args:
        path (PathLike): download path as folder
        cards (Iterable[str]): card given as an ID
    """
    path = Path(path)
    path.mkdir(exist_ok=True)
    card_missings = set()
    for card in cards:
        file = path / f"{card}.png"
        if not file.is_file():
            card_missings.add(card)
    for card in tqdm(card_missings):
        file = path / f"{card}.png"
        url = f'https://arkhamdb.com/bundles/cards/{card}.png'
        req = requests.get(url, timeout=100)
        with file.open("wb") as fid:
            fid.write(req.content)

def refine_images(path: PathLike) -> None:
    """refine images"""
    path = Path(path)
    if not path.is_dir():
        raise FileNotFoundError(path)
    log = path / "blank_files.txt"
    fid = log.open("w", encoding="utf-8")
    for file in tqdm(path.iterdir()):
        if file.suffix.lower() != '.png':
            continue
        if file.stat().st_size == 0:
            file.unlink()
            fid.write(file.name + "\n")
            continue
        image = cv2.imread(str(file))
        image = cv2.resize(image, (300, 419) if image.shape[0]>image.shape[1] else (419, 300))
        cv2.imwrite(str(file), image)
    fid.close()

def main():
    """main function: arguparase should be added"""
    # TODO: argparse
    cards_weak = get_randomweak("randomweak.html")
    cards_player = get_json("json/player_cards.json")
    cards_encounter = get_json("json/encounter_cards.json")
    cards = cards_weak | cards_player | cards_encounter
    download_cards("cards", cards)
    refine_images("cards")

if __name__ == '__main__':
    main()
