#!/bin/bash
echo -e "generate rr_raw.html..."
python3 generate.py raw/rr_raw.html rr_raw.html --raw

echo -e "generate rr.html..."
python3 generate.py raw/rr.html rr.html

echo -e "terminated..."
