import time
import random
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import os
from threading import Thread, Lock

# Define user-agent list
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 10; Generic IoT Device) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; IoT Light Bulb) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.101 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; IoT Security Camera) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1; IoT Thermostat) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.0; IoT Smart Plug) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
]

# Dorking methods
DORKING_METHODS = ["{param}"]

# Lock for thread-safe file writing
file_lock = Lock()

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

# Generate random queries
def generate_random_queries(parameters, num_queries=700):
    if not parameters:
        raise ValueError("Parameters must not be empty.")

    queries = []
    for _ in range(num_queries):
        method = random.choice(DORKING_METHODS)
        param = random.choice(parameters)
        query = method.format(param=param)
        queries.append(query)
    return queries

# Generate spoofed headers with random IPs
def generate_headers():
    spoofed_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "X-Forwarded-For": spoofed_ip,
        "Client-IP": spoofed_ip
    }
    return headers

# Perform dorking for a single query
def perform_dorking(query, max_pages=7, delay=14, results_file="dorking_results.txt"):
    base_url = "https://www.google.com/search?"

    for page_num in range(max_pages):
        start = page_num * 10
        params = {'q': query, 'start': start}
        url = f"{base_url}{urlencode(params)}"
        headers = generate_headers()
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Parse the results page
            soup = BeautifulSoup(response.text, "html.parser")
            search_results = soup.find_all('div', class_='tF2Cxc')

            with file_lock:  # Ensure thread-safe file writing
                with open(results_file, "a") as file:
                    for result in search_results:
                        link = result.find('a', href=True)
                        if link:
                            result_url = link['href']
                            file.write(result_url + "\n")
                            print(f"Saved result: {result_url}")

            # Add random delay with jitter
            sleep_time = delay + random.uniform(-5, 5)
            print(f"Sleeping for {sleep_time:.2f} seconds.")
            time.sleep(sleep_time)
        except requests.exceptions.RequestException as e:
            print(f"Error querying {url}: {e}")
            continue

# Main function
def main():
    # Ensure files exist and load data
    parameters = ensure_file_exists("parameters.txt", ["api", "key", "password", "auth"])
    if not parameters:
        print("No parameters loaded. Please fill 'parameters.txt' with valid entries.")
        return

    # Generate random queries
    queries = generate_random_queries(parameters, num_queries=700)
    results_file = "dorking_results.txt"

    # Start threads for each query
    threads = []
    for query in queries:
        print(f"Starting thread for query: {query}")
        thread = Thread(target=perform_dorking, args=(query, 7, 14, results_file))
        threads.append(thread)
        thread.start()
        time.sleep(random.randint(20, 30))  # Random delay between thread starts

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print("Dorking completed.")

if __name__ == "__main__":
    main()
