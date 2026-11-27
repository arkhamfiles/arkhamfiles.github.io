Write-Output "update card images..."
python download_cards.py

# 2026-12-03: 구 허브 페이지(rule_reference·notes·faq·faq_legacy·errata·taboo·ultimatums·starter_deck·index)는
# 폐기되어 chapters.html로 이동하는 안내 페이지로 대체되었습니다. 다시 생성하면 안내 페이지를 덮어쓰므로 생성 단계를 뺐습니다.
# chapters.html 챕터 2 패널 갱신: python grimoire_generator.py <번역대조표.xlsx> chapters.html

Write-Output "generate test.html..."
python generate.py raw/test.html test.html --nolink

Write-Output "terminated..."
