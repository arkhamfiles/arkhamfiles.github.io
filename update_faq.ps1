Write-Output "pull arkham db data..."
Set-Location ../arkhamdb-json-data
git pull
Set-Location ../arkhamfiles.github.io

Write-Output "generate faq..."
python generate_faq.py

Write-Output "download_cards..."
python download_cards.py