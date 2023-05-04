"""FAQ json generator from google spreadsheet

Please check you have the service key
1) make service account from google cloud
2) generate the service key and download your key as json file
3) if you want, add "spreadsheet_id" for your sheet id
4) give authority of your service e-mail to that spreadsheet
*** make sure that you do not upload service key in Github.
"""

from typing import Dict, List, Tuple, Any, Optional, Union
import re
import json
from pathlib import Path
from os import PathLike
from dataclasses import dataclass
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.http import HttpRequest
# from googleapiclient.errors import HttpError

EntryKey = str

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
    is_link: bool = False
    is_invalid: bool = False
    
    def __init__(self, row_data: List[Dict[str, Any]]):
        raise NotImplementedError()
        # TODO: implement
        # 'userEnteredValue' has one of followings
        # numberValue, stringValue, boolValue, formulaValue, errorValue
        # 'backgroundColorStyle' has 'rgbColor' as ('red', 'green', 'blue')

    # @staticmethod
    # def _is_valid(bg_color) -> bool:
    #     """whether this row is valid, based on the background color

    #     Returns:
    #         bool: True if valid, False if invalid
    #     """
    #     return bg_color[0] < bg_color[1]*1.05 or \
    #            bg_color[0] < bg_color[2]*1.05

class FAQGenerator:
    """faq generator class"""
    def __init__(
        self, path_key: PathLike,
        path_report: Optional[PathLike]=None,
        spreadsheets_id: Optional[str]=None,
        readonly: bool=True
    ):
        """generate class

        Args:
            path_key (PathLike): path of the json file of service key
            path_report (Optional[PathLike], optional): path of report file, no report provided if None. Defaults to None.
            spreadsheets_id (Optional[str], optional): spreadsheets id. do not need if existing in key. Defaults to None.
            readonly (bool, optional): authority scope. Defaults to True.
        """
        self.credentials, self.spreadsheets_id = self._get_google_credentials(path_key, readonly)
        if spreadsheets_id is not None:
            self.spreadsheets_id = spreadsheets_id
        elif not self.spreadsheets_id:
            raise ValueError("spreadsheets id is not given from either key file or init")

        self._service: Resource = build('sheets', 'v4', credentials=self.credentials)
        self.service: Resource = self._service.spreadsheets() # pylint: disable=E1101
        request: HttpRequest = self.service.get(spreadsheetId=spreadsheets_id, includeGridData=False)
        info: Dict[str, Any] = request.execute()
        self.sheets: List[str] = [x['properties']['title'] for x in info['sheets']]
        if 'Note' in self.sheets:
            self.sheets.remove('Note')
        self.faq_entries: Dict[EntryKey, Dict[str, str]] = {}
        self.cards_refered_p: Dict[int, List[EntryKey]] = {}
        self.cards_refered_s: Dict[int, List[EntryKey]] = {}
        if isinstance(path_report, PathLike):
            self._report_stream = open(path_report, "w", encoding='utf-8')
        else:
            self._report_stream = None
    
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
        """
        colrange = _range_tostr(col_start, "A")+":"+_range_tostr(col_end, "ZZ")
        ranges = [f"'{name}'!{colrange}" for name in self.sheets]
        fields = "sheets/data/rowData/values/userEnteredValue"
        fields += ",sheets/data/rowData/values/userEnteredFormat/backgroundColorStyle/rgbColor"
        response = self.service.get(
            spreadsheetId=self.spreadsheets_id, ranges=ranges, fields=fields
        ).execute()
        result = {}
        for name, data in zip(self.sheets, response['sheets']):
            assert len(data['data']) == 1
            rows = []
            for row in data['data'][0]['rowData']:
                rows.append(RowData(row))
            result[name] = rows
        return result
