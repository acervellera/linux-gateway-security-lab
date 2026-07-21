# Stato attuale del progetto

Ultimo aggiornamento operativo: 21 luglio 2026.

## Obiettivo principale

Costruire un gateway fisico Ubuntu nel quale:

- la scheda Wi-Fi interna MediaTek fornisce l'uscita Internet;
- la scheda Wi-Fi USB Realtek crea l'hotspot per dispositivi autorizzati;
- Ubuntu esegue DHCP, DNS, routing, NAT e firewall;
- Suricata e Zeek producono eventi e log;
- Python analizza e correla i log;
- Docker ospita database e dashboard senza gestire il routing principale.

## Percorso verificato

```text
Client 10.42.0.x
  -> Realtek 10.42.0.1
  -> nftables INPUT/FORWARD
  -> Suricata e/o Zeek
  -> analisi Python
  -> NAT/masquerading NetworkManager
  -> MediaTek uplink
  -> router
  -> Internet
```

## Fasi completate

### Fasi 1–5 — Gateway e firewall

Sono stati verificati hardware, topologia, hotspot, DHCP, DNS, forwarding, NAT, WPA2-RSN/CCMP, filtri stateful `INPUT` e `FORWARD`, logging, rollback, servizio systemd dedicato e persistenza dopo reboot.

### Fase 6 — tcpdump

Completata e verificata il 18 luglio 2026. Sono stati osservati DNS, ICMP, handshake TCP, traffico cifrato, traduzione NAT sui due lati e PCAP privato limitato.

```text
Guida:           docs/steps/06-cattura-tcpdump.md
Report pubblico: samples/06-cattura-tcpdump-report.md
Report privato:  reports/06-cattura-tcpdump-private.md
```

### Fase 7 — Suricata IDS

Completata e verificata il 20 luglio 2026.

Risultati:

- Suricata 8.0.3 con AF_PACKET e Hyperscan;
- `HOME_NET` limitato a `10.42.0.0/24`;
- oltre 52.000 regole caricate;
- eventi flow, QUIC, mDNS, DNS, TLS, HTTP, fileinfo e DHCP;
- alert ICMP locale controllato con azione `allowed`;
- avvio su richiesta e rotazione reale di `eve.json`.

```text
Guida:           docs/steps/07-suricata.md
Report pubblico: samples/07-suricata-report.md
Report privato:  reports/07-suricata-private.md
```

### Fase 8 — Zeek

Completata e verificata il 21 luglio 2026.

Risultati:

- Zeek 8.0.9 e ZeekControl;
- sensore standalone sull'interfaccia hotspot;
- rete locale limitata a `10.42.0.0/24`;
- log JSON `conn`, `dns`, `ssl` e `quic`;
- zero drop kernel e zero gap TCP nella prova manuale;
- avvio/arresto on demand e archiviazione gzip.

```text
Guida:           docs/steps/08-zeek.md
Report pubblico: samples/08-zeek-report.md
Report privato:  reports/08-zeek-private.md
```

### Fase 9 — Analisi Python

Completata e verificata il 21 luglio 2026.

Programmi:

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
```

Risultati:

- lettura riga per riga di JSON Lines;
- supporto gzip e standard input;
- statistiche Zeek su connessioni, servizi, byte, durata e stati;
- statistiche Suricata su eventi, flow, alert e anomalie;
- report testuali e JSON;
- indirizzi IP e UID esclusi dai report;
- 23 test automatici superati;
- sessione reale con 33 connessioni Zeek abbinate su 35;
- 101 eventi Suricata correlati;
- delta temporale medio di 0,027 secondi.

```text
Guida:           docs/steps/09-python-log-analysis.md
Report pubblico: samples/09-python-log-analysis-report.md
Report privato:  reports/09-python-log-analysis-private.md
```

## Stato delle fasi

| Fase | Stato | Nota |
|---:|---|---|
| 1. Inventario | COMPLETATA | Hardware, driver e route verificati |
| 2. Topologia | COMPLETATA | Subnet e percorso definiti |
| 3. Hotspot | COMPLETATA | Hotspot, client e rollback verificati |
| 4. DHCP, routing e NAT | COMPLETATA | DHCP, DNS, forwarding e NAT verificati |
| 5. Firewall nftables | COMPLETATA | Filtri, logging, systemd e persistenza verificati |
| 6. tcpdump | COMPLETATA | Protocolli, NAT e PCAP controllato verificati |
| 7. Suricata | COMPLETATA | IDS, regole, alert e rotazione verificati |
| 8. Zeek | COMPLETATA | Log JSON, ZeekControl e archiviazione verificati |
| 9. Python | COMPLETATA | Analisi, report, correlazione e test verificati |
| 10. Docker dashboard | PROSSIMA | Definire schema, importazione e dashboard |
| 11. Test e hardening | DA FARE | Test finali, backup e ripristino |

## Servizi e modalità operative

```text
security-gateway-firewall.service: enabled / active (exited)
Suricata al boot:                   disabled
Suricata durante il laboratorio:    start/stop manuale
Zeek al boot:                       non configurato
Zeek durante il laboratorio:        deploy/stop manuale
hotspot:                            avvio manuale
```

## Materiale pubblico recente

Guide:

- [`steps/07-suricata.md`](steps/07-suricata.md);
- [`steps/08-zeek.md`](steps/08-zeek.md);
- [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md).

Report:

- [`../samples/07-suricata-report.md`](../samples/07-suricata-report.md);
- [`../samples/08-zeek-report.md`](../samples/08-zeek-report.md);
- [`../samples/09-python-log-analysis-report.md`](../samples/09-python-log-analysis-report.md).

## Vincoli di pubblicazione

Non pubblicare password, token, MAC reali, nomi completi delle interfacce, hostname o percorsi personali, IP e porte effimere non necessari, PCAP, query DNS, SNI TLS, certificati, log integrali o valore di `digest_salt`.

Gli output completi restano in `reports/`, esclusa da Git.

## Prossima azione

Passare alla fase 10: definire un formato di importazione idempotente, un database persistente e una dashboard Docker con accesso minimo e volumi in sola lettura.
