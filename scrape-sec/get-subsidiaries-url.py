"""
Get the URL of the subsidiaries link from a given iX SEC filing URL.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

def get_subsidiaries_link_by_text(ix_url):
    headers = {
        "User-Agent": "Me me@example.com",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov"
    }

    if "ix?doc=" in ix_url:
        raw_path = ix_url.split("doc=")[1].split("&")[0]
        target_url = "https://www.sec.gov" + unquote(raw_path)
    else:
        target_url = ix_url

    try:
        response = requests.get(target_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')

        found_link = None

        for tag in soup.find_all('a'):
            link_text = tag.get_text(" ", strip=True).lower()
            
            if "subsidiaries" in link_text:
                found_link = urljoin(target_url, tag.get('href'))
                break
        
        if found_link:
            return found_link
        else:
            return "Link with text 'subsidiaries' not found."

    except requests.exceptions.RequestException as e:
        return f"Network Error: {e}"

input_url = "https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019325000079/aapl-20250927.htm"
subsidiaries_url = get_subsidiaries_link_by_text(input_url)

print(f"{subsidiaries_url}") 
