"""
Get latest SEC 10-K filing URL in iX format from a given SEC browse URL.
"""

import requests
import re

def get_latest_10k_ix_url(browse_url):
    headers = {
        "User-Agent": "Me me@example.com",
        "Accept-Encoding": "gzip, deflate",
    }

    match = re.search(r"CIK=(\d+)", browse_url)
    if not match:
        return "Error: Could not find CIK in URL."

    cik_raw = match.group(1) 
    cik_padded = cik_raw.zfill(10) 

    api_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        recent = data['filings']['recent']
        forms = recent['form']
        
        found_index = -1
        for i, form_type in enumerate(forms):
            if form_type == "10-K":
                found_index = i
                break
        
        if found_index == -1:
            return "No 10-K found."

        acc_num = recent['accessionNumber'][found_index]
        acc_folder = acc_num.replace("-", "")
        
        primary_doc = recent['primaryDocument'][found_index]

        target = (
            f"https://www.sec.gov/ix?doc=/Archives/edgar/data/"
            f"{cik_padded}/{acc_folder}/{primary_doc}"
        )

        return target

    except requests.exceptions.HTTPError as e:
        return f"HTTP Error: {e} (Check your User-Agent)"
    except Exception as e:
        return f"Error: {e}"

input = "https://www.sec.gov/edgar/browse/?CIK=320193&owner=exclude"
output = get_latest_10k_ix_url(input)

print(f"{output}")