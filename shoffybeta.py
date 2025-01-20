import time
import random
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import os
from threading import Thread

# Define user-agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
]

# Dorking methods
DORKING_METHODS = ["{keyword} {param}"]

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
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []

# Function to generate random queries
def generate_random_queries(base_keywords, parameters, num_queries=700):
    if not base_keywords or not parameters:
        raise ValueError("Keywords and parameters must not be empty.")

    queries = []
    for _ in range(num_queries):
        method = random.choice(DORKING_METHODS)
        keyword = random.choice(base_keywords)
        param = random.choice(parameters)
        query = method.format(keyword=keyword, param=param)
        queries.append(query)
    return queries

# Function to perform dorking query
def perform_dorking(query, max_pages=7, delay=14, results_buffer=None):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    base_url = "https://www.google.com/search?"
    results = []

    for page_num in range(max_pages):
        start = page_num * 10
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
                    print(f"Found result: {result_url}")

                    # Store result in buffer (instead of immediate file save)
                    if result_url not in results_buffer:
                        results_buffer.append(result_url)

            print(f"Page {page_num + 1} results processed.")
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Error querying {url}: {e}")
            continue

    return results

# Function to save results periodically (every 2 minutes)
def save_results_periodically(results_buffer, results_file="dorking_results.txt", save_interval=120):
    while True:
        time.sleep(save_interval)
        if results_buffer:
            with open(results_file, "a") as file:
                for result in results_buffer:
                    file.write(result + "\n")
            print(f"Saved {len(results_buffer)} results to {results_file}.")
            results_buffer.clear()  # Clear the buffer after saving

# Main function
def main():
    # Ensure files exist and load data
    parameters = ensure_file_exists("parameters.txt", ["api", "key", "password", "auth"])
    if not parameters:
        print("No parameters loaded. Please fill 'parameters.txt' with valid entries.")
        return

    # Generate random queries
    queries = generate_random_queries(parameters, parameters, num_queries=700)
    results_file = "dorking_results.txt"
    query_log_file = "dorking_queries.txt"

    # Buffer to store results temporarily before saving
    results_buffer = []

    # Start the periodic saving thread
    Thread(target=save_results_periodically, args=(results_buffer, results_file, 120), daemon=True).start()

    # Perform dorking and collect results
    for query in queries:
        print(f"Performing query: {query}")
        with open(query_log_file, "a") as log_file:
            log_file.write(query + "\n")  # Log query

        perform_dorking(query, results_buffer=results_buffer)

        # Random delay between requests
        time.sleep(random.randint(10, 20))

if __name__ == "__main__":
    main()
