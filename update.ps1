Write-Output "generate rule_reference.html..."
python generate.py raw/rule_reference.html rule_reference.html

Write-Output "generate faq.html..."
python generate.py raw/faq.html faq.html --rr rule_reference.html

Write-Output "generate errata.html..."
python generate.py raw/errata.html errata.html --nolink

Write-Output "terminated..."
