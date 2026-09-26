#!/usr/bin/env bash

set -u

TARGET="192.168.0.105"
HTTP_URL="http://${TARGET}"
HTTPS_URL="https://${TARGET}"
WORDLIST="/usr/share/wordlists/dirb/common.txt"

run_attack() {
    local name="$1"
    shift

    echo
    echo "=================================================="
    echo "ATTACK: ${name}"
    echo "=================================================="
    "$@"
    echo
    sleep 3
}

echo "Target: ${TARGET}"
echo "Starting controlled anomaly generation..."
sleep 2

# 1. ICMP probing
run_attack "ICMP scan" \
    ping -c 20 -W 1 "${TARGET}"

# 2. TCP SYN scan
run_attack "TCP SYN scan" \
    sudo nmap -sS -T3 -p 1-1000 "${TARGET}"

# 3. Full TCP port scan
run_attack "Full TCP port scan" \
    sudo nmap -sS -T3 -p- "${TARGET}"

# 4. Service detection
run_attack "Service version detection" \
    nmap -sV -T3 -p 80,443 "${TARGET}"

# 5. OS detection
run_attack "OS detection" \
    sudo nmap -O -T3 "${TARGET}"

# 6. UDP scan
run_attack "UDP scan" \
    sudo nmap -sU -T3 --top-ports 20 "${TARGET}"

# 7. HTTP directory enumeration
if command -v gobuster >/dev/null 2>&1 && [[ -f "${WORDLIST}" ]]; then
    run_attack "HTTP directory enumeration" \
        gobuster dir \
        -u "${HTTP_URL}" \
        -w "${WORDLIST}" \
        -t 10 \
        -q
fi

# 8. HTTPS directory enumeration
if command -v gobuster >/dev/null 2>&1 && [[ -f "${WORDLIST}" ]]; then
    run_attack "HTTPS directory enumeration" \
        gobuster dir \
        -u "${HTTPS_URL}" \
        -w "${WORDLIST}" \
        -t 10 \
        -k \
        -q
fi

# 9. HTTP fuzzing
if command -v ffuf >/dev/null 2>&1 && [[ -f "${WORDLIST}" ]]; then
    run_attack "HTTP URL fuzzing" \
        ffuf \
        -u "${HTTP_URL}/FUZZ" \
        -w "${WORDLIST}" \
        -t 10 \
        -mc all \
        -fs 0 \
        -s
fi

# 10. HTTPS fuzzing
if command -v ffuf >/dev/null 2>&1 && [[ -f "${WORDLIST}" ]]; then
    run_attack "HTTPS URL fuzzing" \
        ffuf \
        -u "${HTTPS_URL}/FUZZ" \
        -w "${WORDLIST}" \
        -t 10 \
        -k \
        -mc all \
        -fs 0 \
        -s
fi

# 11. HTTP request flood
if command -v ab >/dev/null 2>&1; then
    run_attack "HTTP request burst" \
        ab -n 500 -c 20 "${HTTP_URL}/"
fi

# 12. HTTPS request burst
if command -v ab >/dev/null 2>&1; then
    run_attack "HTTPS request burst" \
        ab -n 500 -c 20 -k "${HTTPS_URL}/"
fi

# 13. SYN traffic burst
if command -v hping3 >/dev/null 2>&1; then
    run_attack "TCP SYN burst" \
        sudo hping3 -S -p 80 -c 100 -i u10000 "${TARGET}"
fi

# 14. HTTPS SYN traffic burst
if command -v hping3 >/dev/null 2>&1; then
    run_attack "HTTPS SYN burst" \
        sudo hping3 -S -p 443 -c 100 -i u10000 "${TARGET}"
fi

# 15. HTTP protocol probes
run_attack "HTTP suspicious requests" \
    bash -c '
        for path in \
            "/../../etc/passwd" \
            "/etc/passwd" \
            "/admin" \
            "/administrator" \
            "/wp-admin" \
            "/phpmyadmin" \
            "/.env" \
            "/backup" \
            "/config" \
            "/server-status"
        do
            curl -s -o /dev/null -w "%{http_code} %{url_effective}\n" \
                "http://192.168.0.105${path}"
        done
    '

# 16. HTTPS protocol probes
run_attack "HTTPS suspicious requests" \
    bash -c '
        for path in \
            "/../../etc/passwd" \
            "/etc/passwd" \
            "/admin" \
            "/administrator" \
            "/wp-admin" \
            "/phpmyadmin" \
            "/.env" \
            "/backup" \
            "/config" \
            "/server-status"
        do
            curl -k -s -o /dev/null -w "%{http_code} %{url_effective}\n" \
                "https://192.168.0.105${path}"
        done
    '

echo
echo "=================================================="
echo "All controlled attacks completed."
echo "=================================================="