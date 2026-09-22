#!/bin/bash

request_count=0
max_concurrent_jobs=50

# list of common domains
domains=(
    "https://www.google.com"
    "https://www.youtube.com"
    "https://www.github.com"
    "https://www.linkedin.com"
    "https://www.microsoft.com"
    "https://www.uol.com.br"
    "https://g1.globo.com"
    "http://neverssl.com"
)

user_agents=(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
)

echo "[*] Starting infinite traffic generation..."

while true; do
    random_domain_index=$((RANDOM % ${#domains[@]}))
    selected_domain="${domains[$random_domain_index]}"

    random_agent_index=$((RANDOM % ${#user_agents[@]}))
    selected_user_agent="${user_agents[$random_agent_index]}"

    curl -s -A "$selected_user_agent" -o /dev/null -L "$selected_domain" &

    request_count=$((request_count + 1))

    if [ $((request_count % 5000)) -eq 0 ]; then
        echo "[*] $request_count requests sent..."
    fi

    # Prevents file descriptor exhaustion by limiting active background jobs
    current_running_jobs=$(jobs -r -p | wc -l)
    if [ "$current_running_jobs" -ge "$max_concurrent_jobs" ]; then
        wait -n
    fi
done