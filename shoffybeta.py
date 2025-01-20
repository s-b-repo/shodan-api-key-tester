import time
import random
import requests
import threading
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from queue import Queue
import os

# Define user-agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
]

# Dorking methods
DORKING_METHODS = ["{site} {keyword}"]

# Ensure file exists and prompt user to fill it
def ensure_file_exists(filename, example_data):
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            file.write("\n".join(example_data))
        print(f"Created '{filename}'. Please fill it with relevant data (one entry per line).")
    return read_from_file(filename)

# Read data from a file
def read_from_file(filename):
    try:
        with open(filename, "r") as file:
            data = [line.strip() for line in file if line.strip()]
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []

# Function to generate random queries
def generate_random_queries(base_keywords, sites, parameters, num_queries=1000):
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
def perform_dorking(query, max_pages=5, delay=10, results_queue=None):
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
    # Keywords


    # Ensure parameters.txt and sites.txt exist
    parameters = ensure_file_exists("parameters.txt", ["api", "key", "password", "auth"])
    sites = ensure_file_exists("sites.txt", ["example.com", "pastebin.com", "github.com"])
    base_keywords = parameters

    if not parameters:
        print("No parameters loaded. Please fill 'parameters.txt' with valid entries.")
        return

    if not sites:
        print("No sites loaded. Please fill 'sites.txt' with valid entries.")
        return

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
        time.sleep(random.randint(10, 20))

if __name__ == "__main__":
    main()
