import time
import requests

API_URL = "https://api.jikan.moe/v4/anime"

def best_match(title: str):
    # limit=1 returns the top match only
    r = requests.get(API_URL, params={"q": title, "limit": 1})
    r.raise_for_status()
    data = r.json().get("data", [])
    if not data:
        return None, None
    return data[0].get("mal_id"), data[0].get("title")

def main():
    with open("anime_titles.txt", "r", encoding="utf-8") as f:
        titles = [line.strip() for line in f if line.strip()]

    print("mal_id,name")  # CSV header

    for t in titles:
        mal_id, name = best_match(t)
        if mal_id is None:
            print(f',NOT_FOUND: "{t.replace("\"", "\"\"")}"')
        else:
            safe_name = (name or "").replace('"', '""')
            print(f'{mal_id},"{safe_name}"')

        time.sleep(0.35)  # be polite to Jikan

if __name__ == "__main__":
    main()
