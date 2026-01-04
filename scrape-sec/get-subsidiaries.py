"""
Given a SEC subsidiaries page URL, scrape and return a DataFrame of subsidiaries.
Handles some variations in table formats but is probably still not robust to all.
"""

import requests
import pandas as pd
from io import StringIO
import re

def scrape_subsidiaries_robust(url):
    headers = {
        "User-Agent": "Me me@example.com",
        "Host": "www.sec.gov"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text), header=None)
        
        valid_frames = []
        
        final_col_name_1 = "Entity Name"
        final_col_name_2 = "Jurisdiction"
        headers_captured = False

        for df in tables:
            df_str = df.to_string().lower()
            if 'jurisdiction' in df_str or 'incorporation' in df_str or 'delaware' in df_str:
                df = df.dropna(axis=1, how='all')
                df = df.dropna(axis=0, how='all')
                if df.empty: continue
                first_row_vals = [str(x).lower() for x in df.iloc[0].values]

                is_header_row = any("subsidiary" in x or "name" in x or "jurisdiction" in x or "incorporation" in x for x in first_row_vals)

                if is_header_row:

                    if not headers_captured:
                        raw_1 = str(df.iloc[0, 0])
                        raw_2 = str(df.iloc[0, -1])
                        final_col_name_1 = " ".join(raw_1.split())
                        final_col_name_2 = " ".join(raw_2.split())
                        headers_captured = True
                    
                    # drop the header row
                    df = df[1:]

                if df.shape[1] >= 2:
                    clean_df = pd.DataFrame()

                    clean_df[0] = df.iloc[:, 0]
                    clean_df[1] = df.iloc[:, -1]
                    valid_frames.append(clean_df)

        if valid_frames:

            final_df = pd.concat(valid_frames, ignore_index=True)
            final_df.columns = [final_col_name_1, final_col_name_2]
            col_check = final_df.columns[0]
            final_df = final_df[final_df[col_check].str.contains(re.escape(col_check), case=False, na=False) == False]
            final_df = final_df.dropna(subset=[col_check])
            
            return final_df
        else:
            print("Could not identify subsidiary tables.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# url = "https://www.sec.gov/Archives/edgar/data/2011286/000162828025053993/amtm100325ex211.htm"
url = "https://www.sec.gov/Archives/edgar/data/0000320193/000032019325000079/a10-kexhibit21109272025.htm"
df = scrape_subsidiaries_robust(url)

if df is not None:
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.colheader_justify', 'left')
    
    print(df.to_string(index=False))