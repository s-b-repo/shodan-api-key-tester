import time
import random
import requests
import threading
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from queue import Queue

# Define user-agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
]

# Dorking methods
DORKING_METHODS = [
    "site:{site} {keyword}",
    "{keyword} filetype:txt",
    "{keyword} filetype:log",
    "{keyword} intitle:index.of",
    "{keyword} inurl:api",
    "site:{site} inurl:{keyword}",
    "{keyword} ext:env",
    "{keyword} ext:conf",
    "{keyword} ext:json",
    "site:{site} {keyword} ext:xml",
    "{keyword} inurl:{param}",
    "{keyword} intext:{param}",
    "site:{site} intext:{keyword}",
    "{keyword} site:pastebin.com",
    "{keyword} site:github.com",
    "{keyword} site:gitlab.com",
    "{keyword} \"{param}\"",
    "{keyword} password",
    "{keyword} auth",
    "{keyword} token",
]

# Function to generate random queries
def generate_random_queries(base_keywords, sites, parameters, num_queries=50):
    if not base_keywords or not sites or not parameters:
        raise ValueError("Keywords, sites, and parameters must not be empty.")

    queries = []
    for _ in range(num_queries):
        method = random.choice(DORKING_METHODS)
        keyword = random.choice(base_keywords)
        site = random.choice(sites)
        param = random.choice(parameters)
        query = method.format(keyword=keyword, site=site, param=param)
        queries.append(query)
    return queries

# Function to perform dorking query
def perform_dorking(query, max_pages=5, delay=5, results_queue=None):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    base_url = "https://www.google.com/search?"
    results = []

    for page_num in range(max_pages):
        start = page_num * 10  # Google search results are paginated every 10 results
        params = {'q': query, 'start': start}
        url = f"{base_url}{urlencode(params)}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Parse the results page
            soup = BeautifulSoup(response.text, "html.parser")
            search_results = soup.find_all('div', class_='tF2Cxc')

            for result in search_results:
                link = result.find('a', href=True)
                if link:
                    result_url = link['href']
                    results.append(result_url)
                    print(f"Found result: {result_url}")  # Print the result
                    if results_queue:
                        results_queue.put(result_url)  # Add to queue for saving

            print(f"Page {page_num + 1} results processed.")
            time.sleep(delay)  # Controlled delay
        except requests.exceptions.RequestException as e:
            print(f"Error querying {url}: {e}")
            continue

    return results

# Function to save printed results
def save_printed_results(results_queue, filename="dorking_results.txt", interval=3):
    saved_results = set()

    while True:
        time.sleep(interval)

        new_results = []
        while not results_queue.empty():
            result = results_queue.get()
            if result not in saved_results:
                saved_results.add(result)
                new_results.append(result)

        if new_results:
            with open(filename, "a") as f:
                for result in new_results:
                    f.write(result + "\n")
            print(f"Saved {len(new_results)} results to {filename}.")

# Main function
def main():
    # Keywords, sites, and parameters
    base_keywords = ["shodan key", "API key", "auth token", "password", "secret"]
    sites = [
    "paste.mozilla.org", "ide.geeksforgeeks.org", "pastebin.com", "justpaste.it", "jsfiddle.net",
    "paste.centos.org", "justpaste.it", "jsbin.com", "pastelink.net", "codebeautify.org",
    "controlc.com", "ideone.com", "paste.rohitab.com", "codeshare.io", "paste.opensuse.org",
    "dotnetfiddle.net", "notes.io", "paste2.org", "hastebin.com", "ivpaste.com",
    "justpaste.me", "pastebin.osuosl.org", "bpa.st", "paste.ofcode.org", "paste.ee",
    "dpaste.org", "friendpaste.com", "defuse.ca/pastebin.htm", "dpaste.com", "cl1p.net",
    "pastie.org", "pastecode.io", "pastebin.fr", "jsitor.com", "termbin.com",
    "p.ip.fi", "cutapaste.net", "paste.sh", "paste.jp", "paste-bin.xyz",
    "paste.debian.net", "vpaste.net", "paste.org.ru", "quickhighlighter.com", "commie.io",
    "everfall.com/paste/", "kpaste.net", "pastebin.pt", "n0paste.tk", "tutpaste.com",
    "bitbin.it", "pastebin.fi", "nekobin.com", "paste4btc.com", "pastejustit.com",
    "paste.js.org", "pastefs.com", "paste.mod.gg", "paste.myst.rs"
    ]
    parameters = [
    "api", "key", "password", "token", "auth", "secret", "config", "db",
    "admin", "root", "credentials", "access", "login", "account", "user",
    "username", "email", "smtp", "ftp", "ssh", "oauth", "jwt", "encryption",
    "ssl", "private", "public", "cloud", "aws", "azure", "gcp", "bucket",
    "server", "database", "connection", "auth_token", "session", "cookie",
    "proxy", "cert", "signature", "hash"
]


    # Generate random queries
    queries = generate_random_queries(base_keywords, sites, parameters, num_queries=100)
    results_file = "dorking_results.txt"
    query_log_file = "dorking_queries.txt"

    # Queue to store results
    results_queue = Queue()

    # Start the saving thread
    threading.Thread(target=save_printed_results, args=(results_queue, results_file), daemon=True).start()

    # Perform dorking and collect results
    for query in queries:
        print(f"Performing query: {query}")
        with open(query_log_file, "a") as log_file:
            log_file.write(query + "\n")  # Log query

        perform_dorking(query, results_queue=results_queue)

        # Random delay between requests
        time.sleep(random.randint(5, 10))

if __name__ == "__main__":
    main()
