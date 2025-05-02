import requests
import csv
import json

def fetch_blacklist(domain):
    base_url = f"https://{domain}"
    url = f"{base_url}/api/v1/instance/domain_blocks"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 401:
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

servers_url = "https://api.joinmastodon.org/servers"
response = requests.get(servers_url)
servers_data = response.json()

server_list = servers_data["instances"] if isinstance(servers_data, dict) and "instances" in servers_data else servers_data
domains = [entry.get("domain") for entry in server_list if entry.get("domain")]

output_file = "mastodon_instance_info.csv"
with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "domain", "title", "source_url", "description", "active_month", 
        "languages", "rules", "top_5_trends", "total_users", "total_posts", "blacklist"
    ])

    for domain in domains:
        base_url = f"https://{domain}"
        instance_v2_url = base_url + "/api/v2/instance"
        trends_url = base_url + "/api/v1/trends/tags?limit=5"
        instance_v1_url = base_url + "/api/v1/instance"

        try:
            inst_info = requests.get(instance_v2_url, timeout=10).json()
        except Exception as e:
            print(f"Skipping {domain}: /api/v2/instance ({e})")
            continue

        title = inst_info.get("title", "")
        source_url = inst_info.get("source_url", "")
        description = inst_info.get("description", "")
        active_month = inst_info.get("usage", {}).get("users", {}).get("active_month", "")
        languages = json.dumps(inst_info.get("languages", []), ensure_ascii=False)
        rules = json.dumps(inst_info.get("rules", []), ensure_ascii=False)

        top_trends = []
        try:
            trends_data = requests.get(trends_url, timeout=10).json()
            for tag in trends_data[:5]:
                history = tag.get("history", [{}])[0]
                top_trends.append({
                    "day": history.get("day"),
                    "uses": history.get("uses"),
                    "accounts": history.get("accounts")
                })
        except Exception as e:
            print(f"Warning {domain}: trends ({e})")
        trends_str = json.dumps(top_trends, ensure_ascii=False)

        try:
            inst_stats = requests.get(instance_v1_url, timeout=10).json()
            total_users = inst_stats.get("stats", {}).get("user_count", "")
            total_posts = inst_stats.get("stats", {}).get("status_count", "")
        except Exception as e:
            print(f"Skipping {domain}: /api/v1/instance ({e})")
            continue

        blacklist = fetch_blacklist(domain)

        writer.writerow([
            domain, title, source_url, description, active_month,
            languages, rules, trends_str, total_users, total_posts, blacklist
        ])

print(f"Data collection complete. CSV file saved as '{output_file}'.")
