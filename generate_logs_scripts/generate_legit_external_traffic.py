import requests
import random
import urllib3

# Suppress insecure HTTPS request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

target_ip = "192.168.0.105"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

search_terms = ["john", "admin", "test", "guest", "hello", "user123"]
product_ids = ["1", "2", "3", "4", "5"]
comment_names = ["Alice", "Bob", "Charlie", "David"]
comment_texts = ["Great website!", "Hello, this is a test.", "Nice products.", "Have a good day!"]

while True:
    # Select protocol with a 70% chance for HTTPS and 30% for HTTP
    protocol = random.choices(["https", "http"], weights=[70, 30], k=1)[0]
    base_url = f"{protocol}://{target_ip}"
    
    choice = random.randint(1, 5)
    headers = {"User-Agent": random.choice(user_agents)}

    if choice == 1:
        url = base_url + "/index.php"
        requests.get(url, headers=headers, verify=False)

    elif choice == 2:
        url = base_url + "/users.php"
        requests.get(url, headers=headers, verify=False)

    elif choice == 3:
        url = base_url + "/search.php"
        params = {"q": random.choice(search_terms)}
        requests.get(url, headers=headers, params=params, verify=False)

    elif choice == 4:
        url = base_url + "/products.php"
        params = {"id": random.choice(product_ids)}
        requests.get(url, headers=headers, params=params, verify=False)

    elif choice == 5:
        url = base_url + "/comments.php"
        form_data = {
            "username": random.choice(comment_names),
            "comment": random.choice(comment_texts)
        }
        requests.post(url, headers=headers, data=form_data, verify=False)