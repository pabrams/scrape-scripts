"""
Search arxiv article metadata for word1 and word2, published between fromdate and todate,
 then search their PDF text for pdf_search_phrase.
"""

abstract_words = ["dyson", "sphere"]
fromdate = "199101010000"
todate = "202412312359"
pdf_search_phrase = "extraterrestrial technology"

import requests
import xml.etree.ElementTree as ET
import io
import re
from pypdf import PdfReader
from datetime import datetime

def get_pdf_links(api_url):
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"API Error: {response.status_code}")
        return []

    root = ET.fromstring(response.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    pdf_data = []

    for entry in root.findall('atom:entry', ns):
        published_str = entry.find('atom:published', ns).text
        pub_date = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")

        for link in entry.findall('atom:link', ns):
            if link.get('title') == 'pdf':
                pdf_data.append(link.get('href'))
    return pdf_data

def get_phrase_context(text, phrase, window=5):
    """Extracts context (5 words before/after)"""
    results = []
    clean_text = re.sub(r'\s+', ' ', text)
    words = clean_text.split()
    phrase_parts = phrase.lower().split()
    phrase_len = len(phrase_parts)
    
    for i in range(len(words) - phrase_len + 1):
        segment = [w.lower().strip(".,;:!?\"()[]") for w in words[i : i + phrase_len]]
        if segment == [p.lower() for p in phrase_parts]:
            start = max(0, i - window)
            end = min(len(words), i + phrase_len + window)
            
            snippet_words = words[start:end]
            snippet = " ".join(snippet_words)

            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            snippet = pattern.sub(f"**{phrase}**", snippet)
            results.append(f"...{snippet}...")
            
    return results

def analyze_pdf(pdf_url, phrase):
    headers = {'User-Agent': 'Mozilla/5.0 (Python script; research)'}    
    try:
        response = requests.get(pdf_url, headers=headers, timeout=10)
        if response.status_code != 200: return None
        
        with io.BytesIO(response.content) as f:
            reader = PdfReader(f)
            pages_found = set()
            count = 0
            contexts = []
            
            for p_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if not text: continue
                
                if phrase.lower() in text.lower():
                    pages_found.add(p_num)
                    snippets = get_phrase_context(text, phrase)
                    contexts.extend(snippets)
                    count += text.lower().count(phrase.lower())
            
            return {
                "link": pdf_url,
                "pages": sorted(list(pages_found)),
                "count": count,
                "snippets": contexts
            }
    except Exception as e:
        print(f"Error processing {pdf_url}: {e}")
        return None

def main():
    search_query = f"search_query="
    for i, word in enumerate(abstract_words):
        search_query = f"{search_query}all:{word}+AND+"

    search_query = f"{search_query}submittedDate:[{fromdate}+TO+{todate}]"
    api_url = (
        "http://export.arxiv.org/api/query?"
        f"{search_query}"
        "&max_results=999"
        "&sortBy=submittedDate"
        "&sortOrder=descending"
    )
    links = get_pdf_links(api_url)

    print("| PDF Link | Page Numbers | Sentence Count |")
    print("|--- |--- |--- |---|")

    for link in links:
        
        data = analyze_pdf(link, pdf_search_phrase)
        
        if data and data["count"] > 0:
            page_str = ", ".join(map(str, data["pages"]))
            # context_str = "<br>".join(data["snippets"][:3]) 
            print(f"| {data['link']} | {page_str} | {data['count']} |")

if __name__ == "__main__":
    main()