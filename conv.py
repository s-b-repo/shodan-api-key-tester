import os
import re

def ensure_file_exists(filename, example_data=None):
    """
    Ensures the specified file exists. If not, creates it with example data.
    """
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            if example_data:
                file.write("\n".join(example_data))
        print(f"Created '{filename}'. Please fill it with relevant data if needed.")
    return filename

def read_file(filename):
    """
    Reads all lines from a file and returns them as a list.
    """
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist.")
        return []
    with open(filename, "r") as file:
        return [line.strip() for line in file if line.strip()]

def write_to_file(filename, data):
    """
    Writes a list of strings to a file, one entry per line.
    """
    with open(filename, "w") as file:
        file.write("\n".join(sorted(set(data))))
    print(f"Data saved to '{filename}'.")

def extract_sites_and_parameters(dork_queries):
    """
    Extracts unique sites and parameters from a list of dork queries.
    """
    site_pattern = r"site:([^\s]+)"
    parameter_pattern = r"(api|key|password|token|auth|secret|config|db|admin|credentials|access|login|user|username|email|smtp|ftp|ssh|oauth|jwt|ssl|bucket|server|database|session|cookie|proxy|cert|signature|hash)"

    sites = []
    parameters = []

    for query in dork_queries:
        # Extract sites
        site_match = re.search(site_pattern, query)
        if site_match:
            sites.append(site_match.group(1))

        # Extract parameters
        param_matches = re.findall(parameter_pattern, query)
        parameters.extend(param_matches)

    return sites, parameters

def convert_dork_queries_to_files(input_file, sites_file, parameters_file):
    """
    Converts a list of dork queries into compatible `sites.txt` and `parameters.txt` files.
    """
    dork_queries = read_file(input_file)

    if not dork_queries:
        print("No queries found to process.")
        return

    sites, parameters = extract_sites_and_parameters(dork_queries)

    # Write extracted data to their respective files
    write_to_file(sites_file, sites)
    write_to_file(parameters_file, parameters)

def main():
    print("=== Dork Query Conversion Tool ===")
    
    # Get input file name from the user
    input_file = input("Enter the name of the input file (e.g., dork_queries.txt): ").strip()
    ensure_file_exists(input_file, [
        "site:example.com api",
        "site:github.com password",
        "filetype:log auth",
    ])
    
    # Get output file names from the user
    sites_file = input("Enter the name for the sites output file (e.g., sites.txt): ").strip()
    parameters_file = input("Enter the name for the parameters output file (e.g., parameters.txt): ").strip()

    print("Processing dork queries into compatible files...")
    convert_dork_queries_to_files(input_file, sites_file, parameters_file)
    print(f"Conversion complete. Check '{sites_file}' and '{parameters_file}' for results.")

if __name__ == "__main__":
    main()
