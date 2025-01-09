import time
import random
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup

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
    queries = []
    for _ in range(num_queries):
        method = random.choice(DORKING_METHODS)
        keyword = random.choice(base_keywords)
        site = random.choice(sites)
        param = random.choice(parameters)
        query = method.format(keyword=keyword, site=site, param=param)
        queries.append(query)
    return queries

# Function to perform dorking query and handle pagination
def perform_dorking(query, max_pages=5, delay=5):
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
                    results.append(link['href'])
        
            print(f"Page {page_num + 1} results saved.")
            time.sleep(random.randint(5, 10))  # Random delay between requests
        except requests.exceptions.RequestException as e:
            print(f"Error querying {url}: {e}")
            continue

    return results

# Function to save results every 5 minutes
def save_results_periodically(results, filename="dorking_results.txt", interval=5 * 60, pause_duration=60):
    while True:
        # Wait for the interval (5 minutes)
        time.sleep(interval)
        
        # Save accumulated results
        if results:
            with open(filename, "a") as f:
                for result in results:
                    f.write(result + "\n")
            print(f"Saved results to {filename}. Pausing for {pause_duration} seconds.")
        
        # Clear results after saving
        results.clear()
        
        # Pause for 1 minute
        time.sleep(pause_duration)

# Main function
def main():
    # Keywords, sites, and parameters
    base_keywords = ["shodan key", "API key", "auth token", "password", "secret"]
    sites = ["github.com", "pastebin.com", "gitlab.com", "bitbucket.org", "trello.com"]
    parameters = ["api", "key", "password", "token", "auth"]

    # Generate random queries
    queries = generate_random_queries(base_keywords, sites, parameters, num_queries=100)
    results_file = "dorking_results.txt"
    query_log_file = "dorking_queries.txt"

    # List to store the results
    results = []

    # Perform dorking and collect results
    for query in queries:
        print(f"Performing query: {query}")
        with open(query_log_file, "a") as log_file:
            log_file.write(query + "\n")  # Log query
        page_results = perform_dorking(query)
        if page_results:
            results.extend(page_results)
        
        # Random delay between requests
        time.sleep(random.randint(5, 10))  # Randomized delay

    # Save results periodically in the background
    save_results_periodically(results, filename=results_file)

if __name__ == "__main__":
    main()
