#!/usr/bin/env python3
"""script for download card images from arkhamDB

Instead of load image for each usage, we download necessary images previously.

Currently, we read following cards:
* randomweak.html

"""
import os
import re
import requests

def update_reandomweak():
    re_card = re.compile("{name: '([^']+)', pack: PACK_([A-Z_]+), code: '([^']+)', count: ([0-9]+)[^}]*}")
    # check already exist card:
    files = {
        os.path.splitext(x)[0] for x in os.listdir('cards')
        if os.path.getsize(os.path.join('cards', x)) > 0
    }
    cards = set()
    with open("randomweak.html", encoding='utf-8') as fid:
        for line in fid:
            match = re_card.search(line)
            if match is None:
                continue
            card = match.group(3)
            if card in files:
                continue
            cards.add(match.group(3)) # code
    print(cards)
    for card in cards:
        if card == '00000':
            continue
        url = 'https://arkhamdb.com/bundles/cards/%s.png'%card
        req = requests.get(url)
        with open("cards/%s.png"%card, 'wb') as fid:
            fid.write(req.content)
    

def main():
    update_reandomweak()

if __name__ == '__main__':
    main()