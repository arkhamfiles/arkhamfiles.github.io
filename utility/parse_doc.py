from pathlib import Path
from pdfminer.high_level import extract_text

def main():
    for file in Path("input").iterdir():
        if file.suffix.lower() != ".pdf":
            continue
        text = extract_text(file)
        with Path("output/result.txt").open('w', -1, 'utf-8') as fo:
            fo.write(text)
    pass

if __name__ == '__main__':
    main()
