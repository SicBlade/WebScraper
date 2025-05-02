import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"
}

def fetch_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return url, response.text
    except requests.RequestException as e:
        return url, f"ERROR: {e}"

def search_phrase(html_content, phrase):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ')
    matches = []
    phrase_words = phrase.lower().split()

    # Extract original and lowercase versions of the words for matching
    original_words = text.split()
    lowercase_words = [word.lower() for word in original_words]

    for i in range(len(lowercase_words)):
        word = lowercase_words[i]
        for phrase_word in phrase_words:
            if phrase_word in word:
                snippet = ' '.join(original_words[max(0, i - 5):i + 5])
                matches.append(snippet.strip())
                break  # Skip to next word after finding one match

    return matches

def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    base_netloc = urlparse(base_url).netloc

    for tag in soup.find_all('a', href=True):
        href = tag['href']
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.netloc == base_netloc and parsed.scheme in ['http', 'https']:
            clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path
            links.add(clean_url.rstrip('/'))

    return links

def crawl_website(start_url, phrase, max_pages=30):
    visited = set()
    to_visit = {start_url}
    results = {}

    with tqdm(total=max_pages, desc="🔎 Crawling", unit="page") as progress:
        while to_visit and len(visited) < max_pages:
            current_batch = list(to_visit)[:max_pages - len(visited)]
            to_visit.difference_update(current_batch)

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(fetch_page, url): url for url in current_batch}
                for future in as_completed(futures):
                    url, content = future.result()
                    if not content.startswith("ERROR"):
                        visited.add(url)
                        matches = search_phrase(content, phrase)
                        if matches:
                            results[url] = matches
                        links = extract_links(content, url)
                        to_visit.update(links - visited)

                    progress.update(1)

    return results

def save_results(results, filename, phrase):
    if not filename.endswith('.txt'):
        filename += '.txt'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Search phrase: \"{phrase}\"\n\n")
        for url, matches in results.items():
            f.write(f"URL: {url}\n")
            for match in matches:
                f.write(f"  - {match}\n")
            f.write("\n")

def main():
    print("🌐 Website Phrase Crawler & Search Tool\n")
    start_url = input("Enter the website URL to search (e.g., www.example.com): ").strip()
    if start_url[0] != 'h':
        start_url = 'http://' + start_url
    else:
        print('')
    print(f'\nYou entered {start_url}')
    phrase = input("Enter the word or phrase to search for: ").strip()

    while True:
        try:
            max_pages = int(input("Enter the maximum number of pages to crawl (e.g., 30): ").strip())
            break
        except ValueError:
            print("❗ Please enter a valid integer.")

    filename = input("Enter filename to save results (will be saved as .txt): ").strip()
    print("\n⏳ Starting crawl and search...")
    results = crawl_website(start_url, phrase, max_pages=max_pages)

    if results:
        save_results(results, filename, phrase)
        print(f"\n✅ Done! Matches found on {len(results)} page(s).")
        print(f"📁 Results saved to: {filename if filename.endswith('.txt') else filename + '.txt'}")
    else:
        print("\n❌ No matches found. No file created.")

if __name__ == "__main__":
    main()
