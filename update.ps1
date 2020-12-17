Write-Output "generate rule_reference.html..."
python generate.py raw/rule_reference.html rule_reference.html

Write-Output "generate notes.html..."
python generate.py raw/notes.html notes.html --rr rule_reference.html

Write-Output "generate faq.html..."
python generate.py raw/faq.html faq.html --rr rule_reference.html --faq notes.html

Write-Output "generate errata.html..."
python generate.py raw/errata.html errata.html --nolink

Write-Output "generate taboo.html..."
python generate.py raw/taboo.html taboo.html --nolink

Write-Output "terminated..."
