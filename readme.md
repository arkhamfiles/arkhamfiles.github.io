# <아컴호러 카드게임> 웹 참조 안내서 / FAQ

본 레포지터리는 <아컴호러 카드게임>의 참조 안내서 및 FAQ의 웹 배포를 목표로 합니다.

## 작성 방법

수정은 `raw` 내부에 있는 파일에서 진행하고, python 스크립트를 통하여 자동 변환합니다. 이에 대한 작성 지침은 아래와 같습니다.

* 아이콘은 `[fast]`와 같이 표현합니다. [여기](css/icons.css)에 정의된 아이콘만 사용이 가능합니다.
* 확장 표시자는 `[core]`와 같이 표현합니다. (core, tdl, ptc, tfa, tcu, tde, tic, nc, hw, wh, jf, sc, ...)
* 특성은 `[[마법]]`과 같이 표현합니다.
* 링크는 아래와 같은 규약에 따라 작성시, 자동완성됩니다. (수동으로 해도 됩니다)
  * `X쪽 "~~"`(X는 숫자), `링크 "~~"`: `"~~"`로 변경되며, 같은 문서의 ~~로 자동링크됩니다. ~~는 어떤 항목의 제목입니다. (`X쪽`은 원본 RR과의 호완을 위한 것이고, `링크`로 작성하기를 요청드립니다.)
  * `링크 "~~#id"`: `"~~"`로 변경되며, 같은 문서의 `id`를 id로 가지는 항목으로 링크됩니다. ~~는 아무거나 무관합니다.
  * `링크` --> `참조`: 동일하게 작동하나, 참조 안내서로 링크를 겁니다.
  * `링크` --> `파큐`: 동일하게 작동하나, FAQ로 링크를 겁니다.
* h1, h2, h3, h4의 `id`는 다음 규약에 따라 작성합니다. (h5 이하는 사용하지 않음)
  * `id`가 없으면, 목차에도 등장하지 않고, 링크도 수행하지 않는다는 의미입니다.
  * `_000`의 경우, 목차에 등장하지 않으나, 링크는 수행합니다.
  * `000_`의 경우, 목차에는 등장하지만, 자동링크는 수행하지 않습니다. (같은 제목을 가지는 문서가 여럿인 경우를 위하여)
* FAQ 작성 규약: 아래 사항에 대하여 class 정의가 필요합니다.
  * 특정 확장에서 시작하는 경우: class로 해당 확장을 기입합니다.
    * 예시: 던위치의 유산에서 도입되는 경우, `<p class="dwl">~~~</p>`와 같이 작성하여야 합니다. (`div`로 하여도 무방)
  * 특정 버전에서 추가된 경우: class로 해당 버전을 기입합니다.
    * 예시: 1.1 버전에서 추가/수정된 내용인 경우, `<p class="_1_2">~~</p>`와 같이 작성하여야 합니다. (`div`로 하여도 무방)

## 저작권 / Copyright

참조 안내서, FAQ 등 <아컴호러 카드게임>의 정보의 저작권은 [Fantasy Flight Games](https://www.fantasyflightgames.com/) 및 [코리아보드게임즈](https://www.koreaboardgames.com/)에 있습니다.

The information of *Arkham Horror: The Card Game* such as rule reference, FAQ, is copyrighted by [Fantasy Flight Games](https://www.fantasyflightgames.com/) and [Korea Boardgames](https://www.koreaboardgames.com/_eng/)

## Thanks to

웹페이지는 [ArkhamDB](https://github.com/Kamalisk/arkhamdb)에 기반하여 작성되었습니다. Kam. 및 모든 기여자에게 감사의 말을 올립니다.

The webpage is created based on [ArkhamDB](https://github.com/Kamalisk/arkhamdb). I appreciate Kam. and all contributors of ArkhamDB.
