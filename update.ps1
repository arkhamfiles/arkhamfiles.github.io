Write-Output "generate rule_reference.html..."
python generate.py raw/rule_reference.html rule_reference.html

Write-Output "generate faq.html..."
python generate.py raw/faq.html faq.html --rr rule_reference.html

#Write-Output "generate rr.html..."
#python generate.py raw/rr_ongoing.html rr_ongoing.html

Write-Output "terminated..."
