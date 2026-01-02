import sys
import requests


def main() -> None:
    q = " ".join(sys.argv[1:]).strip()
    if not q:
        print("Usage: python scripts/jikan_find_anime.py Naruto")
        raise SystemExit(1)

    url = "https://api.jikan.moe/v4/anime"
    params = {"q": q, "limit": 5, "sfw": 1, "order_by": "popularity"}

    res = requests.get(url, params=params, timeout=30)
    res.raise_for_status()

    data = res.json().get("data", [])
    if not data:
        print("No results")
        return

    for a in data:
        print(f'{a.get("mal_id")} - {a.get("title")}')


if __name__ == "__main__":
    main()
