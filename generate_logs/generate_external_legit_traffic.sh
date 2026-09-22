#!/usr/bin/env bash

TARGET_IP="192.168.0.105"

# List of common endpoints to simulate real browsing
ENDPOINTS=(
  "/"
  "/index.html"
  "/style.css"
  "/favicon.ico"
  "/robots.txt"
  "/login"
  "/about"
  "/contact"
)

# Common User-Agents (Chrome, Firefox, Safari)
USER_AGENTS=(
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)

echo "Starting traffic generation to $TARGET_IP (HTTP and HTTPS)..."

while true; do
  # Randomly pick protocol, route, and user-agent
  PROTO=$([ $((RANDOM % 2)) -eq 0 ] && echo "http" || echo "https")
  ROUTE=${ENDPOINTS[$RANDOM % ${#ENDPOINTS[@]}]}
  UA=${USER_AGENTS[$RANDOM % ${#USER_AGENTS[@]}]}
  
  URL="${PROTO}://${TARGET_IP}${ROUTE}"
  
  # Run request:
  # -k: ignore self-signed certificate validation (HTTPS)
  # -s: silent mode
  # -o /dev/null: discard response body
  # -w: print HTTP response code
  HTTP_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" -A "$UA" --max-time 5 "$URL")
  
  TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
  echo "[$TIMESTAMP] $PROTO -> $URL | Status: $HTTP_CODE"
  
  # Random pause between 0.5 and 2 seconds
  SLEEP_TIME=$(awk -v min=0.5 -v max=2.0 'BEGIN{srand(); print min+rand()*(max-min)}')
  sleep "$SLEEP_TIME"
done