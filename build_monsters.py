"""Download the D&D 5e SRD monster list once and save a compact monsters.json.

Run once, from the same folder as app.py:
    python build_monsters.py

Only the free SRD monsters are available from these sources (a few hundred).
The rest of the Monster Manual is not freely licensed.
"""
import concurrent.futures as cf
import json
import sys

import requests

HEADERS = {"User-Agent": "SketchQuest/1.0 (hackathon project)"}

# Single-file dumps of the SRD (fast, one request). Tried in order.
FILE_URLS = [
    "https://raw.githubusercontent.com/5e-bits/5e-database/main/src/2014/5e-SRD-Monsters.json",
    "https://raw.githubusercontent.com/5e-bits/5e-database/main/src/5e-SRD-Monsters.json",
]
# Fallback: the public SRD API (one request per monster, so slower).
API_HOST = "https://www.dnd5eapi.co"
API_LISTS = ["/api/2014/monsters", "/api/monsters"]


def fetch_json(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def load_raw():
    for url in FILE_URLS:
        try:
            data = fetch_json(url)
            if isinstance(data, list) and data:
                print(f"Loaded {len(data)} monsters from {url}")
                return data
        except Exception as e:
            print(f"  could not use {url}: {e}")
    for path in API_LISTS:
        try:
            items = fetch_json(API_HOST + path)["results"]
            print(f"Fetching {len(items)} monsters from the API (this takes a minute)...")
            with cf.ThreadPoolExecutor(8) as pool:
                data = list(pool.map(lambda it: fetch_json(API_HOST + it["url"]), items))
            if data:
                print(f"Loaded {len(data)} monsters from {API_HOST}{path}")
                return data
        except Exception as e:
            print(f"  could not use {API_HOST}{path}: {e}")
    sys.exit(
        "Could not download monsters from any source. Check your internet connection, "
        "or place a SRD monsters JSON list in this folder named monsters_raw.json and re-run."
    )


def ac_value(m):
    ac = m.get("armor_class")
    if isinstance(ac, list) and ac:
        return int(ac[0].get("value", 10))
    if isinstance(ac, (int, float)):
        return int(ac)
    return 10


def compact(m):
    speed = m.get("speed")
    speed_str = ", ".join(f"{k} {v}" for k, v in speed.items()) if isinstance(speed, dict) else str(speed or "")
    traits = [a.get("name", "") for a in (m.get("special_abilities") or [])][:3]
    attacks = [a.get("name", "") for a in (m.get("actions") or []) if a.get("name") != "Multiattack"][:3]
    cr = m.get("challenge_rating", 0)
    try:
        cr = float(cr)
    except Exception:
        cr = 0.0
    return {
        "name": m.get("name", "Unknown"),
        "size": m.get("size", ""),
        "type": str(m.get("type", "")).split(" (")[0],
        "cr": cr,
        "ac": ac_value(m),
        "hp": int(m.get("hit_points", 10)),
        "speed": speed_str,
        "features": [f for f in traits + attacks if f],
        "xp": int(m.get("xp", 0) or 0),
    }


def main():
    raw = load_raw()
    seen, out = set(), []
    for m in raw:
        c = compact(m)
        if c["name"].lower() not in seen:
            seen.add(c["name"].lower())
            out.append(c)
    out.sort(key=lambda c: (c["cr"], c["name"]))
    with open("monsters.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"Wrote monsters.json with {len(out)} monsters (CR {out[0]['cr']} to {out[-1]['cr']}).")


if __name__ == "__main__":
    main()
