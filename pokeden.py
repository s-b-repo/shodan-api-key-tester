import shodan

def test_shodan_api_key(api_key):
    """
    Tests if a Shodan API key is valid by attempting to get the account profile information.

    :param api_key: The Shodan API key to test.
    :return: True if the key is valid, False otherwise.
    """
    try:
        # Initialize the Shodan client with the provided API key
        client = shodan.Shodan(api_key)

        # Make a request to fetch account information
        account_info = client.info()

        # If we get here, the key is valid
        print("API Key is valid.")
        print("Account Info:")
        print(f"  Plan: {account_info['plan']}")
        print(f"  Query Credits: {account_info['query_credits']}")
        print(f"  Monitored IPs: {account_info['monitored_ips']}")
        return True

    except shodan.APIError as e:
        # If an error is raised, the API key is likely invalid
        print(f"API Key is invalid: {e}")
        return False

def test_keys_from_file(file_path):
    """
    Tests a list of Shodan API keys from a file.

    :param file_path: Path to the text file containing API keys, one per line.
    """
    try:
        with open(file_path, 'r') as file:
            keys = file.readlines()

        for idx, key in enumerate(keys, start=1):
            key = key.strip()
            if key:
                print(f"\nTesting API Key {idx}: {key}")
                test_shodan_api_key(key)
    except FileNotFoundError:
        print("The specified file was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Test a single API key")
    print("2. Test API keys from a file")

    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        api_key = input("Enter your Shodan API key: ")
        is_valid = test_shodan_api_key(api_key)

        if is_valid:
            print("The provided Shodan API key is valid.")
        else:
            print("The provided Shodan API key is invalid.")

    elif choice == "2":
        file_path = input("Enter the path to the text file containing API keys: ")
        test_keys_from_file(file_path)

    else:
        print("Invalid choice. Please run the script again and select either 1 or 2.")
