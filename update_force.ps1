Write-Output "update card images..."
python download_cards.py

Write-Output "generate rule_reference.html..."
python generate.py raw/rule_reference.html rule_reference.html --force

Write-Output "generate notes.html..."
python generate.py raw/notes.html notes.html --rr rule_reference.html --force

Write-Output "generate faq.html..."
python generate.py raw/faq.html faq.html --rr rule_reference.html --faq notes.html --force
python generate.py raw/faq_legacy.html faq_legacy.html --rr rule_reference.html --faq notes.html --force

Write-Output "generate errata.html..."
python generate.py raw/errata.html errata.html --nolink --force

Write-Output "generate taboo.html..."
python generate.py raw/taboo.html taboo.html --nolink --force

Write-Output "generate ultimatums.html..."
python generate.py raw/ultimatums.html ultimatums.html --nolink --force

Write-Output "generate starter_deck.html..."
python generate.py raw/starter_deck.html starter_deck.html --nolink --force

Write-Output "generate index.html..."
python generate.py raw/index.html index.html --nolink --force

Write-Output "generate test.html..."
python generate.py raw/test.html test.html --nolink --force

Write-Output "generate utility.html..."
python generate.py raw/utility.html utility.html --nolink --force

Write-Output "terminated..."
