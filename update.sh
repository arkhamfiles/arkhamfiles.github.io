#!/bin/bash
echo -e "generate rule_reference.html..."
python3 generate.py raw/rule_reference.html rule_reference.html

echo -e "generate notes.html..."
python3 generate.py raw/notes.html notes.html --rr rule_reference.html

echo -e "generate faq.html..."
python3 generate.py raw/faq.html faq.html --rr rule_reference.html --faq notes.html

echo -e "generate errata.html..."
python3 generate.py raw/errata.html errata.html --nolink

echo -e "generate taboo.html..."
python3 generate.py raw/taboo.html taboo.html --nolink

echo -e "terminated..."
