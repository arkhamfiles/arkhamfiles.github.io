#!/bin/bash
echo -e "generate rule_reference.html..."
python3 generate.py raw/rule_reference.html rule_reference.html

echo -e "generate rr_ongoing.html..."
python3 generate.py raw/rr_ongoing.html rr_ongoing.html

echo -e "terminated..."
