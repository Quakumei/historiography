URL="https://cyberleninka.ru/search?q=%D0%9D%D0%BE%D0%B3%D0%B0%D0%B9%D1%81%D0%BA%D0%B0%D1%8F%20%D0%BE%D1%80%D0%B4%D0%B0"
OUT="links.txt"
TOPAGE=10
python scripts/get_links.py --output_filename $OUT --url_to_parse $URL --topage $TOPAGE
mkdir -p data
cd data && wget -i ../$OUT --wait=1 --waitretry=10
