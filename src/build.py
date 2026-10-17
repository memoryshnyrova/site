"""Собирает ../index.html из template.html и data.json.

Запуск из папки src:   python3 build.py
Нужен Python 3 и Pillow (pip install pillow).

SITE_URL — адрес опубликованного сайта со слешем на конце,
например "https://memory-shnyrova.github.io/site/".
Он нужен для превью в соцсетях (og:image должен быть полным адресом),
для canonical и для sitemap.xml. Пока адреса нет, оставьте пустую строку.
"""
import json, os
from html import escape
from PIL import Image

SITE_URL = ""

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TITLE = "Ольга Шнырова (1957–2025). Сайт памяти"
DESCRIPTION = ("Историк суфражизма и женского движения, основательница Ивановского Центра Гендерных Исследований. "
               "Биография, воспоминания коллег из разных стран, библиография, интервью и лекции.")
OG_TITLE = "Ольга Вадимовна Шнырова (1957–2025)"
OG_DESCRIPTION = ("Биография, воспоминания коллег, карта летних школ и библиография историка феминизма "
                  "и основательницы Ивановского Центра Гендерных Исследований.")
SITE_NAME = "Сайт памяти Ольги Шныровой"


def url(path=""):
    return (SITE_URL + path) if SITE_URL else path


def head():
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Ольга Вадимовна Шнырова",
        "alternateName": ["Ольга Шнырова", "Olga Shnyrova", "Olga Vadimovna Shnyrova"],
        "birthDate": "1957-10-28",
        "deathDate": "2025-11-06",
        "birthPlace": {"@type": "Place", "name": "Иваново"},
        "jobTitle": "историк, директорка Ивановского Центра Гендерных Исследований",
        "alumniOf": ["Ивановский государственный университет", "Ленинградский государственный университет"],
        "knowsAbout": ["суфражизм", "история женского движения", "гендерные исследования", "женская история"],
        "sameAs": [
            "https://independent.academia.edu/oshnyrova",
            "https://scholar.google.com/citations?user=5hZuposAAAAJ",
            "https://arzamas.academy/authors/1074",
            "https://www.limbakh.ru/index.php?id=7708",
        ],
    }
    if SITE_URL:
        person["image"] = url("img/portrait.jpg")
        person["url"] = SITE_URL
    site = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "inLanguage": ["ru", "en"]}
    if SITE_URL:
        site["url"] = SITE_URL
    m = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f"<title>{escape(TITLE)}</title>",
        f'<meta name="description" content="{escape(DESCRIPTION)}">',
        '<meta name="robots" content="index, follow">',
        '<meta name="theme-color" content="#1A1221">',
        '<meta name="color-scheme" content="dark">',
        '<link rel="icon" href="favicon.svg" type="image/svg+xml">',
        f'<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{escape(SITE_NAME)}">',
        f'<meta property="og:title" content="{escape(OG_TITLE)}">',
        f'<meta property="og:description" content="{escape(OG_DESCRIPTION)}">',
        f'<meta property="og:image" content="{url("og-image.jpg")}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="Портрет Ольги Шныровой и надпись «Сайт памяти»">',
        '<meta property="og:locale" content="ru_RU">',
        '<meta property="og:locale:alternate" content="en_US">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{escape(OG_TITLE)}">',
        f'<meta name="twitter:description" content="{escape(OG_DESCRIPTION)}">',
        f'<meta name="twitter:image" content="{url("og-image.jpg")}">',
    ]
    if SITE_URL:
        m.insert(5, f'<link rel="canonical" href="{SITE_URL}">')
        m.append(f'<meta property="og:url" content="{SITE_URL}">')
    m.append('<script type="application/ld+json">' + json.dumps([site, person], ensure_ascii=False) + "</script>")
    return "\n".join(m)


def main():
    t = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    d = open(os.path.join(HERE, "data.json"), encoding="utf-8").read().replace("</", "<\\/")
    img = os.path.join(ROOT, "img")
    dims = {f[:-4]: list(Image.open(os.path.join(img, f)).size) for f in sorted(os.listdir(img)) if f.endswith(".jpg")}
    page = t.replace("/*__DATA__*/null", d).replace("/*__DIMS__*/{}", json.dumps(dims))
    # drop the template's own charset/title/artifact meta; head() supplies them
    for line in ['<meta charset="utf-8">\n', "<title>Ольга Шнырова</title>\n", '<meta name="claude:viewport-fit-sides" content="cover">\n']:
        page = page.replace(line, "", 1)
    style_end = page.index("</style>") + len("</style>")
    html = ("<!doctype html>\n<html lang=\"ru\">\n<head>\n" + head() + "\n" + page[:style_end].replace("<style>", "<style>\nbody{margin:0}", 1)
            + "\n</head>\n<body>\n" + page[style_end:].lstrip() + "\n</body>\n</html>\n")
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    robots = "User-agent: *\nAllow: /\n" + (f"Sitemap: {url('sitemap.xml')}\n" if SITE_URL else "")
    open(os.path.join(ROOT, "robots.txt"), "w").write(robots)
    if SITE_URL:
        open(os.path.join(ROOT, "sitemap.xml"), "w").write(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"  <url><loc>{SITE_URL}</loc></url>\n</urlset>\n")
    print("index.html собран" + ("" if SITE_URL else " (SITE_URL не задан: превью в соцсетях заработает после того, как вы его укажете)"))


if __name__ == "__main__":
    main()
