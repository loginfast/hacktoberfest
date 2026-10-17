"""Find a real photo online for a scene (Wikimedia Commons, no API key needed)."""
import re

import requests

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "SketchQuest/1.0 (hackathon project; contact: none)"}


def find_image(query: str):
    """Return (image_url, credit_text, page_url) for the best match, or None."""
    if not query:
        return None
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": 6,  # File: namespace
        "gsrsearch": f"{query} filetype:bitmap",
        "gsrlimit": 10,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime",
        "iiurlwidth": 900,
    }
    try:
        resp = requests.get(API, params=params, headers=HEADERS, timeout=8)
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
    except Exception:
        return None

    for page in sorted(pages.values(), key=lambda p: p.get("index", 0)):
        info = (page.get("imageinfo") or [{}])[0]
        if info.get("mime") not in ("image/jpeg", "image/png"):
            continue
        url = info.get("thumburl") or info.get("url")
        if not url:
            continue
        meta = info.get("extmetadata", {})
        artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "Unknown")).strip()
        lic = meta.get("LicenseShortName", {}).get("value", "")
        credit = f"{artist[:60]} / {lic} / Wikimedia Commons".strip(" /")
        return url, credit, info.get("descriptionurl", "")
    return None
