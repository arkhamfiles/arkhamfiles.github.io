"""FAQ json generator from google spreadsheet

Please check you have the service key
1) make service account from google cloud
2) generate the service key and download your key as json file
3) if you want, add "spreadsheet_id" for your sheet id
4) give authority of your service e-mail to that spreadsheet
*** make sure that you do not upload service key in Github.
"""

from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import re
import json
from pathlib import Path
from os import PathLike
from dataclasses import dataclass
from collections import defaultdict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.http import HttpRequest
from .html_reader import HTMLReader
from .load_arkhamdb import load_arkhamdb

EntryKey = str

KEY_CARDS = [
    'back_flavor', 'back_text',
    'flavor', 'name', 'is_unique', 'faction_code',
    'subname', 'text', 'traits', 'code',
    'type_code', 'pack_code', 'faq_list'
]

def _range_tostr(index: Union[str, int, None], default: Optional[str]=None) -> str:
    """ help function for range usage
    str] sanity check done
    int] convert 0-based integer index into A-ZZ index (at most ZZ)
    i.e. 0 --> A, 26 --> AA
    None] fill default value (if None, raise error)

    Args:
        index (Union[str, int, None]): index
        default (str): default value for None input

    Returns:
        str: A-ZZ index
    """
    if isinstance(index, str):
        match = re.fullmatch("[A-Z]?[A-Z]", index)
        if match is None:
            raise ValueError(f"index should be A-ZZ, but given is {index}")
        return index
    elif isinstance(index, int):
        if index < 0 or index > 701:
            raise ValueError(f"index should be [0, 700], A-ZZ but {index} is given")
        if index>25:
            return chr(64+index//26) + chr(65+index%26)
        else:
            return chr(65+index)
    if default is None:
        raise ValueError(f"default should be given for invalid index {index}")
    return default

@dataclass(unsafe_hash=True)
class RowData:
    """Class for row data from spreadsheet information"""
    text: str = ''
    card_id: str = ''
    faq_level: str = ''
    date: str = ''
    is_formula: bool = False
    is_valid: bool = True
    
    def __init__(self, row_data: List[Dict[str, Dict[str, Any]]]):
        super().__init__()
        ### change below index if spreadsheet order is changed
        cell_faq = row_data[6] if len(row_data) > 6 else {}
        cell_cardid = row_data[2] if len(row_data) > 6 else {}
        cell_level = row_data[3] if len(row_data) > 6 else {}
        cell_date = row_data[4] if len(row_data) > 6 else {}
        ### then...
        key, self.text = self._get_cell(cell_faq)
        self.is_formula = key == 'formulaValue'
        if 'backgroundColorStyle' in cell_faq.get('userEnteredFormat', {}):
            color = cell_faq['userEnteredFormat']['backgroundColorStyle']['rgbColor']
            self.is_valid = self._is_valid(color.get('red', 0), color.get('green', 0), color.get('blue', 0))
        if not self.text:
            self.is_valid = False
        _, self.card_id = self._get_cell(cell_cardid, False)
        _, self.faq_level = self._get_cell(cell_level, False)
        _, self.date = self._get_cell(cell_date, False) # TODO: check data type if necessary
    
    @staticmethod
    def _get_cell(
        cell: Dict[str, Dict[str, Any]],
        get_formula: bool=True,
        raise_error: bool=True
        ) -> Tuple[str, str]:
        """get cell value from spreadsheet cell format
        Cell should contains following dict:
            userEnteredValue
                AnyKey: str (1 item only)

        Args:
            cell (Dict[str, Dict[str, str]]): input dict
            get_formul (bool, optional): if get raw formula. Default to True
            raise_error (bool, optional): check error. Defaults to True.

        Returns:
            str: key
            str: text (force conversion as str)
        """
        if 'userEnteredValue' in cell:
            assert len(cell['userEnteredValue']) == 1
            key, value = next(iter(cell['userEnteredValue'].items()))
            if raise_error and key == 'errorValue':
                raise ValueError(f"error while capturing row_data: {value}")
            if key == 'formulaValue' and not get_formula:
                return key, str(next(iter(cell['effectiveValue'].values())))
            return key, str(value)
        else:
            return '', ''

    @staticmethod
    def _is_valid(red: float, green: float, blue: float) -> bool:
        return red < green*1.05 or red < blue*1.05

class FAQGenerator:
    """faq generator class"""
    def __init__(
        self, path_key: PathLike,
        path_qna: PathLike, path_notes: PathLike,
        path_errata: PathLike, path_rr: PathLike,
        path_report: Optional[PathLike]=None,
        spreadsheets_id: Optional[str]=None,
        readonly: bool=True
    ):
        self._report_stream = None
        """generate class

        Args:
            path_key (PathLike): path of the json file of service key
            path_qna (PathLike): path of qna html file
            path_notes (PathLike): path of rule notes html file
            path_errata (PathLike): path of errata html file
            path_rr (PathLike): path of rr html file
            path_report (Optional[PathLike], optional): path of report file, no report provided if None. Defaults to None.
            spreadsheets_id (Optional[str], optional): spreadsheets id. do not need if existing in key. Defaults to None.
            readonly (bool, optional): authority scope. Defaults to True.
        """
        self.credentials, self.spreadsheets_id = self._get_google_credentials(path_key, readonly)
        if spreadsheets_id is not None:
            self.spreadsheets_id = spreadsheets_id
        elif not self.spreadsheets_id:
            raise ValueError("spreadsheets id is not given from either key file or init")
        
        path_qna = Path(path_qna)
        path_notes = Path(path_notes)
        path_errata = Path(path_errata)
        path_rr = Path(path_rr)
        if not path_qna.is_file():
            raise FileNotFoundError(path_qna)
        if not path_notes.is_file():
            raise FileNotFoundError(path_notes)
        if not path_errata.is_file():
            raise FileNotFoundError(path_errata)
        if not path_rr.is_file():
            raise FileNotFoundError(path_rr)

        self._service: Resource = build('sheets', 'v4', credentials=self.credentials)
        self.service: Resource = self._service.spreadsheets() # pylint: disable=E1101
        request: HttpRequest = self.service.get(spreadsheetId=self.spreadsheets_id, includeGridData=False)
        info: Dict[str, Any] = request.execute()
        self.sheets: List[str] = [x['properties']['title'] for x in info['sheets']]
        if 'Note' in self.sheets:
            self.sheets.remove('Note')
           
        self.entries_qna = HTMLReader(path_qna).refine_qna()
        self.entries_notes = HTMLReader(path_notes).refine_notes(path_notes.name)
        self.entries_errata = HTMLReader(path_errata).refine_errata(path_errata.name)
        self.entries_rr = HTMLReader(path_rr).refine_notes(path_rr.name)
        
        if isinstance(path_report, PathLike):
            self._report_stream = open(path_report, "w", encoding='utf-8')
    
    def __del__(self):
        if self._report_stream is not None and not self._report_stream.closed:
            self._report_stream.close()

    @staticmethod
    def _get_google_credentials(path_key: PathLike, readonly: bool=True) -> Tuple[Credentials, str]:
        """get google credentials from sevice account, using OAuth2

        Args:
            path_key (PathLike): path of the json file of service key
            readonly (bool, optional): authority scope. Defaults to True.

        Returns:
            Credentials: google credentials for auth
            str: get spreadsheet id if exists
        """
        path_key = Path(path_key)
        if not path_key.exists():
            raise FileNotFoundError(path_key)
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        if readonly:
            scopes[0] += '.readonly'
        with path_key.open(encoding='utf-8') as f:
            service_account_info = json.load(f)
        creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        if 'spreadsheet_id' in service_account_info:
            sheet_id = service_account_info['spreadsheet_id']
        else:
            sheet_id = ''
        return creds, sheet_id
    
    def _write_report(self, format_text: str, *args, **kwargs) -> int:
        """write report with report IO (only if opened)

        Args:
            format_text (str): format text, as python formatting

        Returns:
            bool: number of length to write in stream
        """
        if self._report_stream is None or self._report_stream.closed:
            return 0
        return self._report_stream.write(format_text.format(args=args, kwargs=kwargs))

    def get_data(self, col_start: Union[int, str, None]=None,
                 col_end: Union[int, str, None]=None
                 ) -> Dict[str, List[RowData]]:
        """get data from given sheet

        Args:
            sheet_name (str): name of sheet
            col_start (Union[int, str, None], optional): start column. A-based str or 0-based integer. Defaults to None (free).
            col_end (Union[int, str, None], optional): end column. A-based str or 0-based integer. Defaults to None (free).
        
        Return:
            Dict[str, List[RowData]]: row data as dictionary
                key: sheet name
                value: list of row data
        """
        colrange = _range_tostr(col_start, "A")+":"+_range_tostr(col_end, "ZZ")
        ranges = [f"'{name}'!{colrange}" for name in self.sheets]
        fields = "sheets/data/rowData/values/userEnteredValue"
        fields += ",sheets/data/rowData/values/effectiveValue"
        fields += ",sheets/data/rowData/values/userEnteredFormat/backgroundColorStyle/rgbColor"
        response = self.service.get(
            spreadsheetId=self.spreadsheets_id, ranges=ranges, fields=fields
        ).execute()
        result = {}
        for name, data in zip(self.sheets, response['sheets']):
            assert len(data['data']) == 1
            rows = []
            for row in data['data'][0]['rowData']:
                rows.append(RowData(row.get('values', [])))
            result[name] = rows
        return result
    
    def generate_faq(self, path_json: PathLike) -> Dict[str, Dict[str, str]]:
        # TODO: logger
        path_json = Path(path_json)
        data = self.get_data()
        result: Dict[str, Dict[str, str]] = {}
        regex_formula = re.compile(r"='?([^']+)?(?:'!)?[A-Z]{1,2}([0-9]+)")
        regex_faq = re.compile(r"(?:https://arkhamfiles.github.io/)?([a-zA-Z_]+).html#([a-zA-Z0-9_]+)#?([0-9]+)?")
        regex_qna = re.compile(r"[Qq]:[ ]?(.+)\n[Aa]:[ ]?(.+)")
        for sheet_name, rows in data.items():
            for i, row in enumerate(rows[1:]):
                if not row.is_valid:
                    continue
                if row.is_formula:
                    match = regex_formula.fullmatch(row.text)
                    if match is None:
                        continue
                    x, y = match.groups(sheet_name)
                    key = "{}_{:04d}".format(x, int(y))
                    if key in result:
                        result[key]['card_list'].append(row.card_id)
                    else:
                        result[key] = {'card_list': [row.card_id]}
                    continue
                key = f"{sheet_name}_{i:04d}"
                item = {
                    'level': row.faq_level,
                    'date': row.date,
                    'card_list': row.card_id.split(),
                    'text': row.text
                }
                if not item['level'] or not item['text']: # sanity
                    continue
                match = regex_qna.search(item.get('text', ''))
                if match is not None:
                    item['question_text'], item['answer_text'] = match.groups()
                    item.pop('text')
                match = regex_faq.search(item.get('text', ''))
                if match is not None:
                    doc, name, num = match.groups()
                    if doc in ['faq', 'faq_legacy']:
                        if name not in self.entries_qna:
                            print(f"FAQ is given but key is unknown: {item['text']} for {row.card_id}")
                        else:
                            num = int(num)-1 if isinstance(num, str) else 0
                            item['question_text'], item['answer_text'] = self.entries_qna[name][2][num]
                            item.pop('text')
                    elif doc == 'notes':
                        if name not in self.entries_notes:
                            print(f"notes is given but key({name}) is unknown: {item['text']} for {row.card_id}")
                        else:
                            if num is not None:
                                print('notes does not support number pick.')
                            item['text'] = self.entries_notes[name][2]
                    elif doc == 'errata':
                        if name not in self.entries_errata:
                            print(f"errata is given but key({name}) is unknown: {item['text']} for {row.card_id}")
                        else:
                            num = int(num)-1 if isinstance(num, str) else 0
                            item['text'] = self.entries_errata[name][2][num]
                    elif doc == 'rule_reference':
                        if name not in self.entries_rr:
                            print(f"rr is given but key({name}) is unknown: {item['text']} for {row.card_id}")
                        else:
                            if num is not None:
                                print('notes does not support number pick.')
                            item['text'] = self.entries_rr[name][2]
                    else:
                        print(f"unknown link is given: {item['text']}")
                if key in result:
                    item['card_list'].extend(result[key]['card_list'])
                result[key] = item
        keys_del = set()
        for key, value in result.items():
            if 'level' not in value:
                keys_del.add(key)
        for key in keys_del:
            result.pop(key)
        with path_json.open("w", encoding="utf-8") as fp:
            json.dump(result, fp, ensure_ascii=False, indent=4)
        return result
    
    def generate_card(
            self, data: Dict[str, Dict[str, str]],
            path_db: PathLike,
            path_player: PathLike, path_encounter: PathLike,
            overwrite_encounter: bool=False
        ) -> None:
        """generate card information for faq entries

        Args:
            data (Dict[str, Dict[str, str]]): data from faq generator
            path_db (PathLike): local path of arkhamdb-json-data repository
            path_player (PathLike): player card json
            path_encounter (PathLike): encounter card json
            overwrite_encounter (bool, optional): if you want to reset encounter json. Defaults to False.
        """
        path_player = Path(path_player)
        path_encounter = Path(path_encounter)
        
        # load card data from arkhamdb-json-data repo
        data_player = load_arkhamdb(path_db, 'player', 'ko')
        data_encounter = load_arkhamdb(path_db, 'encounter', 'ko')
        
        # we only use several key...
        for key, value in data_player.items():
            data_player[key] = {k: v for k, v in value.items() if k in KEY_CARDS}
        for key, value in data_encounter.items():
            data_encounter[key] = {k: v for k, v in value.items() if k in KEY_CARDS}
        
        # extract only faq-related cards
        faq_lists: Dict[str, List[str]] = defaultdict(list)
        for key, entry in data.items():
            for card in entry['card_list']:
                faq_lists[card].append(key)
        data_player = {k: v for k, v in data_player.items() if k in faq_lists}
        data_encounter = {k: v for k, v in data_encounter.items() if k in faq_lists}
        
        # update encounter data from current information if necessary
        if not overwrite_encounter and path_encounter.is_file():
            with path_encounter.open("r", encoding="utf-8") as fp:
                data_enc: Dict[str, Dict[str]] = json.load(fp)
            for key, value in data_enc.items():
                if key in data_encounter:
                    for k, v in value.items():
                        data_encounter[key][k] = v
        
        # always update faq_list key
        for key, faq in faq_lists.items():
            if key in data_player:
                data_player[key]["faqs"] = faq
            if key in data_encounter:
                data_encounter[key]["faqs"] = faq
        
        # then, write
        with path_player.open("w", encoding='utf-8') as fp:
            json.dump(data_player, fp, indent=4, ensure_ascii=False, sort_keys=True)
        with path_encounter.open("w", encoding='utf-8') as fp:
            json.dump(data_encounter, fp, indent=4, ensure_ascii=False, sort_keys=True)

if __name__ == "__main__":
    gen = FAQGenerator("../api_key.json", "../raw/faq_legacy.html", "../raw/notes.html", "../raw/errata.html")
    data = gen.generate_faq("example.json")
    gen.generate_card(data, "../../arkhamdb-json-data", "player.json", "encounter.json")