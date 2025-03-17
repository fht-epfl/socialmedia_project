import requests
import csv
import time
import json

def fetch_instance_info(domain):
    """
    Fetch instance information from a Mastodon server using the /api/v2/instance endpoint.
    """
    base_url = f"https://{domain}"
    url = f"{base_url}/api/v2/instance"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching instance info for {domain}: {e}")
        return None

def fetch_blacklist(domain):
    """
    Fetch the domain blacklist from a Mastodon server using the /api/v1/instance/domain_blocks endpoint.
    """
    base_url = f"https://{domain}"
    url = f"{base_url}/api/v1/instance/domain_blocks"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 401:
            # If authorization is required, skip fetching the blacklist.
            print(f"{domain}: domain_blocks requires authorization, skipping.")
            return ""
        response.raise_for_status()
        blocks = response.json()
        if isinstance(blocks, list):
            return " | ".join([entry.get("domain", "") for entry in blocks])
        else:
            return ""
    except Exception as e:
        print(f"Error fetching blacklist for {domain}: {e}")
        return ""

def process_instance_info(instance_info):
    """
    Flatten the instance info dictionary.
    For dictionary or list values, convert them to a JSON string so all fields are stored.
    """
    processed = {}
    for key, value in instance_info.items():
        if isinstance(value, (dict, list)):
            try:
                processed[key] = json.dumps(value, ensure_ascii=False)
            except Exception as e:
                processed[key] = str(value)
        else:
            processed[key] = value
    return processed

def main():
    # 1. Fetch the Mastodon server list from the official directory API.
    server_list_url = "https://api.joinmastodon.org/servers"
    try:
        response = requests.get(server_list_url, timeout=10)
        response.raise_for_status()
        servers_data = response.json()
        # Extract server domains from the returned data
        if isinstance(servers_data, list):
            server_list = [entry.get("domain") or entry.get("url") or entry.get("name") for entry in servers_data]
        elif "instances" in servers_data:
            server_list = [entry.get("domain") or entry.get("name") for entry in servers_data["instances"]]
        elif "servers" in servers_data:
            server_list = [entry.get("domain") or entry.get("name") for entry in servers_data["servers"]]
        else:
            print("Unable to recognize server list format.")
            server_list = []
    except Exception as e:
        print(f"Failed to fetch server list: {e}")
        server_list = []
    
    # If the server list is empty, use a backup list (for demonstration purposes)
    if not server_list:
        server_list = [
            "mastodon.social",
            "mastodon.online"
        ]
    
    print(f"Fetched {len(server_list)} Mastodon instances.")
    
    all_rows = []
    all_keys = set()
    
    # 2. Process each server: fetch instance info and blacklist data.
    for domain in server_list:
        if not domain:
            continue
        print(f"Processing {domain} ...")
        instance_info = fetch_instance_info(domain)
        if instance_info is None:
            continue
        processed_info = process_instance_info(instance_info)
        # Add server domain as an identifier.
        processed_info["server"] = domain
        # Fetch the blacklist and add it to the result.
        blacklist = fetch_blacklist(domain)
        processed_info["blacklist"] = blacklist
        
        all_rows.append(processed_info)
        all_keys.update(processed_info.keys())
        
        # Respect rate limits by pausing for 1 second between requests.
        time.sleep(1)
    
    # 3. Write all data to a CSV file using the union of all keys as the CSV header.
    csv_filename = "mastodon_instance_info.csv"
    all_keys = list(all_keys)
    all_keys.sort()  # Sort keys alphabetically for consistency.
    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_keys)
            writer.writeheader()
            for row in all_rows:
                writer.writerow(row)
        print(f"Data saved to {csv_filename}.")
    except Exception as e:
        print(f"Failed to write CSV file: {e}")

if __name__ == "__main__":
    main()
