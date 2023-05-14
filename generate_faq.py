"""script for faq generation
TODO: arguparser
"""

from pathlib import Path
from faq_generator.faq_generator import FAQGenerator

def main():
    if not Path("../arkhamdb-json-data").is_dir():
        print("please clone arkhamdb-json-data before launch this. (will be updated via script).")
    
    generator = FAQGenerator(
        "api_key.json",
        "raw/faq_legacy.html",
        "raw/notes.html",
        "raw/errata.html",
        "raw/rule_reference.html"
    )
    data = generator.generate_faq("json/faq.json")
    generator.generate_card(
        data,
        "../arkhamdb-json-data",
        "json/player_cards.json",
        "json/encounter_cards.json"
    )

if __name__ == "__main__":
    main()
