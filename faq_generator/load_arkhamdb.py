"""load arkhamdb json file

This script do not load data from arkhamDB directly.
It just load data from data from github repo like
https://github.com/Kamalisk/arkhamdb-json-data
or forked repo (from local folder)
"""

from typing import Dict, Optional, List, Any
import json
import re
from os import PathLike
from pathlib import Path

def load_arkhamdb(
    path_db: PathLike,
    load_type: str = 'all',
    translation: Optional[str] = None
) -> Dict[str, Dict[str, str]]:
    """load data from arkhamDB data local repository

    Args:
        path_db (PathLike): local repository path
        load_type (str, optional): load data type, 'player', 'encounter', 'all'. Defaults to 'all'.
        translation (Optional[str], optional): if given, translation data is loaded (ex: 'es'). Defaults to None.

    Returns:
        Dict[str, Dict[str, str]]: key: card id, value: metadata
        * regardless of translation, all metadata is given.
    """
    load_type = load_type.lower()
    if load_type == 'all':
        regex_filename = re.compile(r"[a-z]+(?:_encounter)?\.json")
    elif load_type == 'player':
        regex_filename = re.compile(r"[a-z]+\.json")
    elif load_type == 'encounter':
        regex_filename = re.compile(r"[a-z]+_encounter\.json")
    else:
        raise ValueError(f"load_type should be player, encounter, or all. given: {load_type}")
    path_db = Path(path_db)
    if not path_db.is_dir():
        raise FileNotFoundError(path_db)
    path_original = path_db / "pack"
    if not path_original.is_dir():
        raise FileNotFoundError(f"{path_original} not exists. It maybe not arkhamdb-json-data repository?")
    path_translation = path_original if translation is None else path_db / "translations" / translation / "pack"
    if not path_translation.is_dir():
        raise FileNotFoundError(f"{path_translation} not exists. Check translation input: {translation}")
    
    files_original: List[Path] = []
    for folder_cycle in path_original.iterdir():
        if not folder_cycle.is_dir():
            continue
        for file in folder_cycle.iterdir():
            match = regex_filename.fullmatch(file.name)
            if match is not None:
                files_original.append(file)
    
    result: Dict[str, Dict[str, str]] = {}
    for file_original in files_original:
        with file_original.open(encoding='utf-8') as fid:
            data: List[Dict[str, Any]] = json.load(fid)
            data = {x['code']: x for x in data}
        file_translation = path_translation / file_original.parent.name / file_original.name
        if file_translation.is_file():
            with file_translation.open(encoding='utf-8') as fid:
                data_tr: List[Dict[str, Any]] = json.load(fid)
            for card in data_tr:
                for key, value in card.items():
                    if key == 'code':
                        continue
                    if key in data[card['code']] and data[card['code']][key] != value:
                        data[card['code']][key+"_real"] = data[card['code']][key]
                    data[card['code']][key] = value
        result.update(data)
    return result

if __name__ == '__main__':
    data = load_arkhamdb("../../arkhamdb-json-data", 'player', 'ko')
    print(data['02147'])
    # with open("card.json", "w", encoding='utf-8') as fid:
    #     json.dump(data, fid, ensure_ascii=False, indent=4, sort_keys=True)