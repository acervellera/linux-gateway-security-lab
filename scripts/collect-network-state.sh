#!/usr/bin/env bash

# Raccoglie lo stato della rete senza modificarlo.
# Il report può contenere indirizzi IP, nomi di interfaccia e regole firewall:
# revisionarlo prima di pubblicarlo.

set -u
set -o pipefail

OUTPUT_DIR="${1:-reports}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
HOST="$(hostname 2>/dev/null || printf 'unknown-host')"
OUTPUT_FILE="${OUTPUT_DIR}/network-state-${HOST}-${TIMESTAMP}.txt"

mkdir -p "${OUTPUT_DIR}"

run_section() {
    local title="$1"
    shift

    {
        printf '\n================================================================================\n'
        printf '%s\n' "${title}"
        printf 'Comando: '
        printf '%q ' "$@"
        printf '\n================================================================================\n'
    } >> "${OUTPUT_FILE}"

    if "$@" >> "${OUTPUT_FILE}" 2>&1; then
        return 0
    fi

    local exit_code=$?
    printf '\n[comando terminato con codice %s]\n' "${exit_code}" >> "${OUTPUT_FILE}"
    return 0
}

{
    printf 'Linux Gateway Security Lab - Network State Report\n'
    printf 'Timestamp UTC: %s\n' "${TIMESTAMP}"
    printf 'Hostname: %s\n' "${HOST}"
    printf 'Utente: %s\n' "${USER:-unknown}"
    printf 'Kernel: %s\n' "$(uname -r 2>/dev/null || printf 'unknown')"
} > "${OUTPUT_FILE}"

run_section "Interfacce - formato breve" ip -br link
run_section "Indirizzi IPv4" ip -4 -br address
run_section "Indirizzi IPv6" ip -6 -br address
run_section "Tabella di routing IPv4" ip -4 route
run_section "Tabella dei vicini IPv4/IPv6" ip neigh
run_section "Statistiche delle interfacce" ip -s link

if command -v nmcli >/dev/null 2>&1; then
    run_section "NetworkManager - dispositivi" nmcli -p device status
    run_section "NetworkManager - profili" nmcli -p connection show
    run_section "NetworkManager - profili attivi" nmcli -p connection show --active
else
    printf '\n[nmcli non disponibile]\n' >> "${OUTPUT_FILE}"
fi

if command -v sysctl >/dev/null 2>&1; then
    run_section "IPv4 forwarding" sysctl net.ipv4.ip_forward
fi

if command -v nft >/dev/null 2>&1; then
    if [ "${EUID}" -eq 0 ]; then
        run_section "nftables ruleset" nft list ruleset
    elif command -v sudo >/dev/null 2>&1; then
        run_section "nftables ruleset" sudo -n nft list ruleset
    else
        printf '\n[nft disponibile, ma servono privilegi per leggere il ruleset completo]\n' >> "${OUTPUT_FILE}"
    fi
fi

if command -v iw >/dev/null 2>&1; then
    run_section "Interfacce wireless" iw dev
    run_section "Dominio normativo wireless" iw reg get
fi

if command -v docker >/dev/null 2>&1; then
    run_section "Docker - reti" docker network ls
fi

if command -v virsh >/dev/null 2>&1; then
    run_section "libvirt - reti" virsh net-list --all
fi

printf '\nReport creato: %s\n' "${OUTPUT_FILE}"
printf 'Revisionare il file prima di pubblicarlo: può contenere dati della rete locale.\n'
