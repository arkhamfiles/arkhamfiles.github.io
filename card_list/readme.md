# Card List Generator

이 폴더는 arkhamdb-json-data에서 부터 arkhamDB like한 웹 파일을 제공하기 위한 제작용 프로그램 입니다. 일반적으로 json 파일이 upstream에 반영되지 않은 상황에서, 작업해야 하는 상황에서 활용합니다.

사용법은 아래와 같습니다. 간단히만 작성하오니, 사용이 필요한 경우 문의 주시거나 확인후 사용하세요.

## 간단한 사용법

 1. [arkhamdb-json-data](https://github.com/elkeinkrad/arkhamdb-json-data) 를 clone합니다. 추천 경로는 본 리포와 동일한 경로에 두는 것입니다. 커스텀도 가능합니다.
 2. python generate.py 를 실행합니다.
 3. outputs.json 파일이 잘 생성되었는지 확인합니다. 확인만 하면 됩니다.
 4. dist 에 들어가서 확인.


## 트러블 슈팅

* python이 안되요: python 3만 호환됩니다. 버전은 적당히 높으면 됩니다. 3.6이나 3.7이면 될거에요.
* 커스텀 json에서 하고싶어요: 알아서 json 수정해서 하세요 ㅎㅎ; 위 코드는 영어와 한글을 동시에 크롭하니까 그 두개만 수정하면 됩니다.
* 다른 사이클을 하고싶어요: generate.py 파일의 `cycle = 'tic'`을 바꾸면 됩니다.
* 파일이 이상하게 보여요: 위에 파일 다 챙겼나요?

## 크레딧

* card_list.html 의 템플릿은 Bires님께서 만들어 주셨습니다.
