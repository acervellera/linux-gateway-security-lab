# Roadmap completa

## Obiettivo generale

Costruire un gateway Ubuntu attraverso cui far passare il traffico di dispositivi autorizzati, osservarlo in modo difensivo, analizzarne i log con Python e visualizzare i risultati tramite servizi Docker.

## Architettura finale

```text
Client autorizzato
      |
      v
Hotspot Realtek USB
      |
      v
Ubuntu gateway
    |-- DHCP / DNS locale
    |-- routing e NAT
    |-- nftables INPUT/FORWARD
    |-- servizio systemd dedicato
    |-- tcpdump
    |-- Suricata
    |-- Zeek
    |-- Python
    `-- Docker
      |
      v
MediaTek interna
      |
      v
Internet
```

## Sequenza delle fasi

| Fase | Documento | Risultato richiesto | Stato attuale |
|---:|---|---|---|
| 1 | [`steps/01-inventario-hardware-rete.md`](steps/01-inventario-hardware-rete.md) | Identificare hardware, driver, interfacce e uplink | COMPLETATO |
| 2 | [`steps/02-topologia-e-indirizzamento.md`](steps/02-topologia-e-indirizzamento.md) | Definire nomi, subnet, gateway e percorso | COMPLETATO |
| 3 | [`steps/03-hotspot-realtek.md`](steps/03-hotspot-realtek.md) | Creare un hotspot stabile | COMPLETATO |
| 4 | [`steps/04-dhcp-routing-nat.md`](steps/04-dhcp-routing-nat.md) | Verificare DHCP, DNS, forwarding, NAT e Wi-Fi | COMPLETATO |
| 5 | [`steps/05-firewall-nftables.md`](steps/05-firewall-nftables.md) | Applicare filtro stateful, log e persistenza | COMPLETATO |
| 6 | [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md) | Verificare filtri, protocolli, NAT e PCAP | COMPLETATO |
| 7 | [`steps/07-suricata.md`](steps/07-suricata.md) | Produrre e verificare avvisi IDS | COMPLETATO |
| 8 | [`steps/08-zeek.md`](steps/08-zeek.md) | Generare log di rete strutturati | COMPLETATO |
| 9 | [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md) | Leggere, analizzare e correlare i log | COMPLETATO |
| 10 | [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md) | Salvare e visualizzare dati | PROSSIMO |
| 11 | [`steps/11-test-hardening-backup.md`](steps/11-test-hardening-backup.md) | Test finali, hardening, backup e ripristino | DA FARE |

## Fasi 1–5 — Gateway e firewall

Sono stati verificati hardware, topologia, hotspot, DHCP, DNS, forwarding, NAT, sicurezza WPA2-RSN/CCMP, filtri `INPUT` e `FORWARD`, logging, rollback, servizio systemd dedicato e persistenza dopo riavvio.

Componenti pubblici principali:

```text
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
```

## Fase 6 — tcpdump

Completata e verificata il 18 luglio 2026. Sono stati verificati DNS, ICMP, handshake TCP, traffico cifrato, confronto prima e dopo il NAT, PCAP privato limitato e compatibilità con AppArmor.

```text
Report pubblico: samples/06-cattura-tcpdump-report.md
Report privato:  reports/06-cattura-tcpdump-private.md
```

## Fase 7 — Suricata

Completata e verificata il 20 luglio 2026. Suricata 8.0.3 è stato configurato come IDS passivo sull'interfaccia hotspot con `HOME_NET` limitato alla rete di laboratorio, regole caricate, alert controllato e rotazione reale di `eve.json`.

```text
Report pubblico: samples/07-suricata-report.md
Report privato:  reports/07-suricata-private.md
```

## Fase 8 — Zeek

Completata e verificata il 21 luglio 2026. Zeek 8.0.9 è stato configurato come sensore standalone con log JSON `conn`, `dns`, `ssl` e `quic`, zero drop kernel nella prova manuale e gestione on demand tramite ZeekControl.

```text
Report pubblico: samples/08-zeek-report.md
Report privato:  reports/08-zeek-private.md
```

## Fase 9 — Python

Completata e verificata il 21 luglio 2026.

Sono stati realizzati:

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/tests/test_phase9.py
```

Risultati principali:

- lettura streaming di JSON Lines e gzip;
- statistiche Zeek e Suricata;
- report testuali e JSON privi di IP grezzi e UID;
- 23 test automatici superati;
- correlazione reale di 101 eventi Suricata;
- 33 connessioni Zeek abbinate su 35;
- delta temporale medio di 0,027 secondi.

```text
Report pubblico: samples/09-python-log-analysis-report.md
Report privato:  reports/09-python-log-analysis-private.md
```

## Fase 10 — Database e dashboard Docker

Docker verrà usato per importazione, database, API, dashboard e volumi. I log e i report saranno montati in sola lettura quando possibile. Non verranno usati container privilegiati senza una necessità dimostrata.

Percorso previsto:

1. definire uno schema minimo;
2. importare i report JSON;
3. rendere l'importazione idempotente;
4. usare volumi persistenti;
5. esporre una dashboard soltanto sulla rete prevista;
6. documentare backup e ripristino.

## Fase 11 — Test e hardening

- uplink assente;
- isolamento tra client;
- casi `ct state invalid`;
- servizi IDS fermi;
- spazio e rotazione log;
- backup e ripristino;
- rimozione sicura del laboratorio.

## Criterio di completamento del progetto

Il progetto è completato quando un dispositivo autorizzato:

1. si collega all'hotspot;
2. riceve configurazione IP corretta;
3. usa Ubuntu come unico gateway;
4. raggiunge Internet tramite MediaTek;
5. è filtrato da nftables;
6. genera log Suricata e Zeek;
7. compare nei report Python;
8. compare nella dashboard Docker;
9. continua a funzionare dopo test controllati;
10. può essere disconnesso e ripristinato con procedure documentate.
