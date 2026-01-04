"""
Get search results page for a given Nasdaq ticker from the SEC website.
"""

import requests

def get_modern_sec_url(ticker):
    headers = {
        "User-Agent": "Me me@example.com",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov"
    }

    try:
        json_url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(json_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        target_cik = None
        target_title = None
        ticker_clean = ticker.upper().strip()


        for entry in data.values():
            if entry['ticker'] == ticker_clean:

                target_cik = entry['cik_str'] 
                target_title = entry['title']
                break

        if not target_cik:
            return f"Ticker {ticker} not found in SEC index."

        final_url = (
            f"https://www.sec.gov/edgar/browse/?"
            f"CIK={target_cik}&owner=exclude"
        )

        return {
            "Company": target_title,
            "CIK": target_cik,
            "Target URL": final_url
        }

    except requests.exceptions.RequestException as e:
        return f"Network Error: {e}"

result = get_modern_sec_url("AAPL")

if isinstance(result, dict):
    print(f"{result['Target URL']}")
else:
    print(result)