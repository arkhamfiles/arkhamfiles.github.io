"""HTML file parser from html generator

target files:
raw/faq_legacy.html
raw/notes.html
raw/errata.html

All other files are not tested, but may work.
"""

from typing import Dict, List, Tuple, Optional, Any, TypeVar
from os import PathLike
from pathlib import Path
import re
from bs4 import BeautifulSoup
from bs4.element import Tag

# ItemType = Tuple[str, List[str], str, str] # tag, class, content, style if any
ItemType = Any
ContentType = Tuple[int, str, List[ItemType]] # level(h1, h2, h3...), title, list of items
DataType = Dict[str, ContentType] # key=id

Self = TypeVar("Self", bound="HTMLReader")

class HTMLReader(DataType):
    def __init__(self, path: PathLike):
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(path)
        super().__init__()
        self._read(path)
    
    def _read(self, path: Path):
        with path.open(encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, 'html.parser', from_encoding='utf-8')
        tagname = re.compile(r"h[0-9]")
        tag: Optional[Tag] = soup.find('html')
        curr_id: Optional[str] = None
        while True:
            tag: Optional[Tag] = tag.find_next([tagname, "p", "li", "td"])
            if tag is None:
                break
            elif tag.name and tag.name[0] == 'h':
                if 'id' in tag.attrs:
                    curr_id = tag['id']
                    level = int(tag.name[1])
                    text = ''.join(map(lambda x: str(x), tag.contents))
                    self[curr_id] = level, text, []
                else:
                    curr_id = None
            elif curr_id is None: # pass if curr_id is None with contents
                continue
            else:
                info = tag.attrs.get('class', [])
                text = ''.join(map(lambda x: str(x), tag.contents))
                style = tag.attrs.get('style', '')
                self[curr_id][2].append((tag.name, info, text, style))
    
    def refine_notes(self, url: Optional[str]="notes.html") -> Self:
        """refine rule notes html

        Args:
            url (Optional[str]): url of rule notes for autometic link
        """
        if url is not None and url and url[-1] == '/':
            url = url[:-1]
        for key, value in self.items():
            # TODO: check ItemType
            result = ''
            for tag, classes, text, _ in value[2]:
                if 'example' in classes:
                    result += '\n<b>예시</b>: ' + text
                elif tag == 'li':
                    result += '\n * ' + text
                else:
                    result += '\n' + text
            result = result[1:]
            if url is not None:
                result += f' 자세한 사항은 <a href="{url+"#"+key}">규칙 보충 해설 {value[1]}</a>을 참고해주세요.'
            if result:
                self[key] = (self[key][0], self[key][1], result)
        return self
    
    def refine_qna(self) -> Self:
        """refine QnA style
        itemtype: Tuple[str, str] -- question & answer
        """
        unnecessary_keys = set()
        for key, value in self.items():
            # TODO: check ItemType
            result = []
            question, answer = '', ''
            for tag, classes, text, _ in value[2]:
                if 'question' in classes:
                    if question and answer:
                        result.append((question, answer))
                    elif question or answer:
                        assert f"question: {question}, answer: {answer}"
                    question = text
                    answer = ''
                elif 'answer' in classes:
                    answer = text
                elif 'example' in classes:
                    answer += '\n<b>예시</b>: ' + text
                elif tag == 'li':
                    answer += '\n * ' + text
            if question and answer:
                result.append((question, answer))
            if result:
                self[key] = (self[key][0], self[key][1], result)
            else:
                unnecessary_keys.add(key)
        for key in unnecessary_keys:
            self.pop(key)
        return self
    
    def refine_errata(self, url: Optional[str]="errata.html") -> Self:
        for key, value in self.items():
            result = []
            curr_txt = ''
            for tag, _, text, _ in value[2]:
                if tag == 'td':
                    if curr_txt:
                        curr_txt += "\n<b>변경 문구:</b> " + text.strip()
                        if url is not None:
                            curr_txt += f' 자세한 사항은 <a href="{url+"#"+key}">정오표</a>를 참고해주세요.'
                        # TODO: span style 추가
                        result.append(curr_txt)
                        curr_txt = ''
                    else:
                        curr_txt += "이 카드는 수정사항이 있습니다. <b>기존 문구:</b> " + text.strip()
            if result:
                self[key] = (self[key][0], self[key][1], result)
        return self

if __name__ == "__main__":
    reader = HTMLReader("../raw/faq_legacy.html")
    reader.refine_qna()
    print(reader['FAQ11'])
    print(reader['FAQ_rDatTE'])
    
    reader = HTMLReader("../raw/notes.html")
    reader.refine_notes()
    print(reader["Rulings_1_2"])
    print(reader["Rulings_2_4"])
    
    reader = HTMLReader("../raw/errata.html")
    reader.refine_errata()
    print(reader['05313'])