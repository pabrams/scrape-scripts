"""
Get interpol red notices for a list of arrest warrant countries.
Looks up country codes via pycountry.
"""

from curl_cffi import requests
import pycountry
import time
import json
import sys

ALL_NOTICES = []

def get_iso_code(country_name):
    try:
        results = pycountry.countries.search_fuzzy(country_name)
        if results:
            return results[0].alpha_2
    except LookupError:
        return None
    return None

def fetch_interpol_red_notices(country_name):
    country_code = get_iso_code(country_name)
    if not country_code:
        print(f"[-] Country code not found for: {country_name}", file=sys.stderr)
        return

    url = "https://ws-public.interpol.int/notices/v1/red"
    params = {
        "arrestWarrantCountryId": country_code,
        "resultPerPage": 20
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            impersonate="chrome" 
        )

        if response.status_code == 200:
            data = response.json()

            embedded = data.get('_embedded', {})
            notices = embedded.get('notices', [])

            for notice in notices:
                notice['arrestWarrantCountryId'] = country_code
                ALL_NOTICES.append(notice)

        else:
            print(f"{response.status_code} at {response.url}", file=sys.stderr)

    except Exception as e:
        print(f"[-] Error: {e}", file=sys.stderr)

def main():
    filtered_data = []
    countries = [
        "Canada"
        ]
    
    for country in countries:
        fetch_interpol_red_notices(country)
        time.sleep(2) 


    for entry in ALL_NOTICES:
        if entry.get("arrestWarrantCountryId") not in (entry.get("nationalities") or []):
            filtered_entry = {
                "date_of_birth": entry.get("date_of_birth"),
                "nationalities": entry.get("nationalities"),
                "entity_id": entry.get("entity_id"),
                "forename": entry.get("forename"),
                "name": entry.get("name"),
                "arrestWarrantCountryId": entry.get("arrestWarrantCountryId")
            }
            filtered_data.append(filtered_entry)

    sorted_data = sorted(filtered_data, key=lambda x: x['arrestWarrantCountryId'])
    print(json.dumps(sorted_data, indent=2))

if __name__ == "__main__":
    main()
