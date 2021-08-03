# <아컴호러 카드게임> 웹 참조 안내서 / FAQ

본 레포지터리는 <아컴호러 카드게임>의 참조 안내서 및 FAQ의 웹 배포를 목표로 합니다.

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
    * beautifulsoup4, html5lib 을 설치하여야 합니다.
    * python 3.6 이하라면, dataclasses를 설치하여야 합니다.
    * 폰트 생성을 위해 fontforge를 설치하여야 합니다.
      * windows: fontforge 설치 위치의 bin 폴더(eg. C:\Program Files (x86)\FontForgeBuilds\bin)를 PATH 시스템 변수에 추가하여야 합니다.
      * ubuntu: TODO
  * 아래 스크립트를 실행합니다. (현재 폴더에서 실행해야함)
    * windows: powershell에서 `.\update.ps1`을 실행합니다.
    * ubuntu: terminal에서 `bash update.sh`를 실행합니다.
  * 주의
    * 수정 시간을 기반으로 수정 여부를 판단합니다. 자동 스킵되는 경우 시스템 시간을 확인해주세요.
    * github는 font 파일의 변경 사항을 추적하지 못합니다. font에 변경사항이 없으나 생성한 경우, 되도록 font 파일의 revert를 요청드립니다.
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

## 저작권 / Copyright

참조 안내서, FAQ 등 <아컴호러 카드게임>의 정보의 저작권은 [Fantasy Flight Games](https://www.fantasyflightgames.com/) 및 [코리아보드게임즈](https://www.koreaboardgames.com/)에 있습니다.

The information of *Arkham Horror: The Card Game* such as rule reference, FAQ, is copyrighted by [Fantasy Flight Games](https://www.fantasyflightgames.com/) and [Korea Boardgames](https://www.koreaboardgames.com/_eng/)

## Thanks to

웹페이지는 [ArkhamDB](https://github.com/Kamalisk/arkhamdb)에 기반하여 작성되었습니다. Kam. 및 모든 기여자에게 감사의 말을 올립니다.

The webpage is created based on [ArkhamDB](https://github.com/Kamalisk/arkhamdb). I appreciate Kam. and all contributors of ArkhamDB.
