# <아컴호러 카드게임> 허브

본 레포지터리는 <아컴호러 카드게임> 허브 관리를 위한 레포지터리 입니다. 자세한 것은 깃허브 페이지로 생성된 웹페이지를 참고해주세요.

<아컴호러 카드게임> 허브는 <아컴호러 카드게임>의 정식 라이선스 및 한국 내 독점 판권을 보유한 코리아보드게임즈의 공식 사이트입니다. 본 사이트는 코리아보드게임즈로부터 관리를 위탁받아 네이버 아컴파일즈 카페에서 운영하고 있으며, <아컴호러 카드게임> 한국어판의 번역진이 주축이 되어 번역 및 관리를 하고 있습니다. 

This repository is generated for "the hub of Arkham horror The Card Game", Korean language. For more detail, please check the website generated using the github-pages.

"The hub of Arkham horror The Card Game" is the offical site of Koreaboardgames, the sole agent of AHLCG. This repository is maintained by the arkhamfiles naver cafe entrusted by koreaboardgames. If you want to contact us, please contact any contributors of this repository, e-mail address in the website, or write issue on this repository.

## License / Copyright

본 레포지터리에 있는 내용은 기본적으로 저작권이 있는 항목입니다. 사용에 주의를 가지시길 바랍니다. 웹페이지 형태가 아닌 RAW 파일의 형태더라도 저작권이 있음을 유의하시길 바랍니다. 저작권에 관해서는, 웹페이지에 명시된 항목을 참고해 주시길 바랍니다.

"본 사이트 및 본 사이트의 모든 내용은 코리아보드게임즈의 사전 동의 없이 복사, 복제, 재출판, 업로드, 게시, 전송, 배포 또는 2차적 저작물 생성 등에 이용될 수 없습니다. 다만, 코리아보드게임즈는 이용자에게 본 사이트의 텍스트, 사진, 소리, 파일, 링크 등의 정보(“자료”)에 접근하고 이용할 수 있는, 그리고 본 사이트를 개인적, 비상업적인 용도로만 사용할 수 있는 비독점적, 양도 불가능한 제한적 권리를 부여합니다."

추가로, 본 웹사이트 기본 골조는 ArkhamDB에서 가져왔습니다. (좌우 구성 및 목차 나열 및 아래 footnote 위치 등). 본 항목에 대해서는 저작권을 가지고 있지 않음을 밝힙니다. 이 자리를 빌어 Kalmalisk를 포함한 ArkhamDB의 모든 기여자들에게 감사의 말을 올립니다.

유일한 예외로, **python script**는 MIT license 조건 하에서 사용하여도 됩니다. 본 license를 적용받는 파일은 `html_generator` 폴더 내의 `defines.py`를 제외한 파일, `generate.py`, `generate_icon.py` 입니다. 이 것이 코드 내에 있는 텍스트 그 자체를 사용해도 된다는 의미는 아닌 것은 명심하시길 바랍니다.

(english translation: korean has priority)

All contents in this repository has license. Please be careful if you want to use. If you want to use the contents, please check the license in the webpage.

The structure of this website comes from ArkhamDB (structure, content, footnotes). We have NO license about them. In this page, we sincerely thanks to all contributors of ArkhamDB including Kalmalisk.

Some python scripts will be distributed as MIT license: all files in `html_generator` (except `defines.py`), `generator.py`, `generate_icon.py`. You can check the license file in `html_generator/license`.

## 할일

* fontforge font 작성 코드 fontTools로 변경 (fontforge 없어도 되게)
* QnA 쪽 전처리 코드 수정

## 작성 방법

수정은 **[raw](raw) 내부에 있는 파일**에서 진행하고, python 스크립트를 통하여 자동 변환합니다. raw 폴더 내부에 있는 html 파일의 작성 지침은 아래와 같습니다. 혹여나 수정을 하시는 경우, raw 폴더 안에 있는 파일만 수정한 후 자동 제작하거나, maintainer에게 알려주시길 바랍니다. 외부 파일만 수정한 후, pull하는 경우 해당 수정 내용이 실수로 revert될 수 있습니다.

* 아이콘은 `[fast]`와 같이 표현합니다.
  * 자세한 리스트는 [여기](html_generator/defines.py#L6)에 정의된 아이콘만 사용이 가능합니다.
  * ICON에 포함된 리스트는 자동변환 리스트입니다. ICON_REDIRECT에 포함된 리스트는 편이를 위해 변환되는 것입니다. (예를 들어, free가 권장되며 fast는 free로 자동으로 바뀜)
* 확장 표시자는 `[core]`와 같이 표현합니다. (core, tdl, ptc, tfa, tcu, tde, tic, nc, hw, wh, jf, sc, ...)
  * 자세한 리스트는 [여기](html_generator/defines.py#L43)를 참고해주세요.
  * [SYMBOLS](html_generator/defines.py#29)에 포함된 확장은 아이콘으로 작성됩니다. 그렇지 않은 경우, 글로 표현됩니다.
* 특성은 `[[마법]]`과 같이 표현합니다.
* 링크는 아래와 같은 규약에 따라 작성시, 자동완성됩니다. (수동으로 해도 됩니다)
  * `X쪽 "~~"`(X는 숫자), `링크 "~~"`: `"~~"`로 변경되며, 같은 문서의 ~~로 자동링크됩니다. ~~는 어떤 항목의 제목입니다. (`X쪽`은 원본 RR과의 호완을 위한 것이고, `링크`로 작성하기를 요청드립니다.)
  * `링크 "~~#id"`: `"~~"`로 변경되며, 같은 문서의 `id`를 id로 가지는 항목으로 링크됩니다. ~~는 아무거나 무관합니다.
  * `링크` --> `참조`: 동일하게 작동하나, 참조 안내서로 링크를 겁니다.
  * `링크` --> `파큐`: 동일하게 작동하나, 규칙 보충 해설로 링크를 겁니다.
  * 기타 FAQ/금기 리스트에 해당하는건 만들지 않았으나, 필요하면 만들도록 하겠습니다.
* h1, h2, h3, h4의 `id`는 다음 규약에 따라 작성합니다. (h5 이하는 사용하지 않음)
  * `id`가 없으면, 목차에도 등장하지 않고, 링크도 수행하지 않는다는 의미입니다.
  * `_000`의 경우, 목차에 등장하지 않으나, 링크는 수행합니다.
  * `000_`의 경우, 목차에는 등장하지만, 자동링크는 수행하지 않습니다. (같은 제목을 가지는 문서가 여럿인 경우를 위하여)
* FAQ 작성 규약: 아래 사항에 대하여 class 정의가 필요합니다.
  * 특정 확장에서 시작하는 경우: class로 해당 확장을 기입합니다.
    * 예시: 던위치의 유산에서 도입되는 경우, `<p class="dwl">~~~</p>`와 같이 작성하여야 합니다. (`div`로 하여도 무방)
    * 작성되지 않은 경우 기본판으로 간주합니다.
  * 특정 버전에서 추가된 경우: class로 해당 버전을 기입합니다.
    * 예시: 1.1 버전에서 추가/수정된 내용인 경우, `<p class="V1_2">~~</p>`와 같이 작성하여야 합니다. (`div`로 하여도 무방)
    * 작성되지 않은 경우 1.0 버전으로 간주합니다.
  * 위 두 사항은 "한국어판만 보기", "최신버전 강조하기" 기능에 활용됩니다.

## 자동 생성하기

본 문서는 `raw/***.html` 파일에서 python 스크립트를 이용하여 자동으로 실제 문서를 작성합니다.
  * depencency: python3+ 에서 작동합니다. 2.7에서는 작동하지 않습니다.
    * beautifulsoup4, html5lib, requests 를 설치하여야 합니다.
    * python 3.6 이하라면, dataclasses를 설치하여야 합니다.
    * 폰트 생성을 위해 fontforge를 설치하여야 합니다.
      * windows: fontforge 설치 위치의 bin 폴더(eg. C:\Program Files (x86)\FontForgeBuilds\bin)를 PATH 시스템 변수에 추가하여야 합니다.
      * ubuntu: TODO
  * 아래 스크립트를 실행합니다. (현재 폴더에서 실행해야함)
    * windows: powershell에서 `.\update.ps1`을 실행합니다.
    * ubuntu: terminal에서 `bash update.sh`를 실행합니다. (추후 업데이트 예정)
  * 주의
    * 수정 시간을 기반으로 수정 여부를 판단합니다. 자동 스킵되는 경우 시스템 시간을 확인해주세요.
    * github는 font 파일의 변경 사항을 추적하지 못합니다. font에 변경사항이 없으나 생성한 경우, 업로드 해도 그만 안해도 그만입니다. 편한대로 하세요!
  * ~~이렇게 써도 제가 하겠죠 아마~~
    
## 폰트 수정하기

본 문서에서는 svg 파일을 폰트로 제작합니다. 폰트제작 스크립트는 [여기](generate_icon.py)를 참고하세요. 폰트를 수정하는 방법은 아래와 같습니다.

 * svg파일을 [svgs](svgs)에 추가합니다. 파일명은 상관 없습니다. (svg만 가능하니, png 등은 변환 요망)
   * svg 파일은 되도록 가로-세로 크기가 같도록 합니다. 가로가 길면 먹힐 가능성이 있습니다.
 * [info.json](svgs/info.json) 파일을 수정합니다. `char`는 맵핑하려는 문자, `name`은 html 내부에서 사용할 코드명, `path`는 파일명을 의미합니다.
   * a-z는 사이클, A-Z는 돌아온, 0-9는 독시/스타터를 계획하고 있습니다.
 * [defines.py](html_generator/defines.py) 파일을 수정합니다. `SYMBOLS`에 추가하면 됩니다. (`name`, 실제 이름) 으로 작성해야 합니다.
   * 특정 확장판인 경우 `EXPANSION`에도 추가하도록 합시다. 작성시 발매 순서에 맞추어야 합니다. 이는 FAQ 작성시에 필터링을 위해 활용됩니다.
 * generate를 수행하면 자동으로 폰트 및 symbols.css가 생성됩니다. fontforge library가 설치되어, python과 연동되어야 합니다.
   * windows인 경우, PATH를 지정하면 ffpython을 활용합니다.
   * ubuntu는 fontforge를 잘 깔아야 합니다. 시도 안해봄.

## python 가상환경 설정
 * powershell 실행
 * `pip install virtualenv`
 * `python -m venv venv`
 * `venv/Scripts/Activate.ps1`
   * 권한 문제로 오류가 나는 경우, 관리자 권한으로 powershell 실행 후, `Set-ExecutionPolicy Unrestricted`
 * `pip install -r requrements.txt`
 * `./(name of script).ps1`