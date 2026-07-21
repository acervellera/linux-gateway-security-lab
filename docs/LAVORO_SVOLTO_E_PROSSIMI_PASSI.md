# Lavoro svolto e prossimi passi

## Funzione del documento

Questo file riassume l'evoluzione reale del gateway fisico Ubuntu. Per lo stato più aggiornato usare [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md); per comandi e rollback usare le guide in [`steps`](steps).

## Gateway fisico

```text
Dispositivo autorizzato
  -> Realtek USB AP
  -> Ubuntu gateway
  -> nftables INPUT e FORWARD
  -> Suricata e Zeek
  -> analisi Python
  -> NAT/masquerading
  -> MediaTek uplink
  -> Internet
```

## Fasi 1–5 completate

Sono stati verificati inventario hardware, topologia, hotspot, DHCP, DNS, forwarding, NAT, WPA2-RSN/CCMP, firewall stateful, logging, rollback, servizio systemd e persistenza dopo reboot.

## Fase 6 completata — tcpdump

Completata il 18 luglio 2026. Verificati filtri BPF, DNS, ICMP, handshake TCP, traffico cifrato, NAT sui due lati, decremento TTL e PCAP privato limitato.

```text
Report pubblico: samples/06-cattura-tcpdump-report.md
Report privato:  reports/06-cattura-tcpdump-private.md
```

## Fase 7 completata — Suricata

Completata il 20 luglio 2026. Suricata 8.0.3 è stato configurato sull'interfaccia hotspot con `HOME_NET` limitato alla rete di laboratorio, regole caricate, eventi applicativi, alert ICMP controllato e rotazione reale.

```text
Report pubblico: samples/07-suricata-report.md
Report privato:  reports/07-suricata-private.md
```

## Fase 8 completata — Zeek

Completata il 21 luglio 2026. Zeek 8.0.9 è stato configurato come sensore standalone con log JSON, rete locale esplicita, `digest_salt` personalizzato, cattura senza drop kernel e gestione on demand tramite ZeekControl.

```text
Report pubblico: samples/08-zeek-report.md
Report privato:  reports/08-zeek-private.md
```

## Fase 9 completata — Python

Completata e verificata il 21 luglio 2026.

### Codice

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/tests/test_phase9.py
```

### Risultati

- elaborazione streaming di JSON Lines e gzip;
- statistiche verificate sui log Zeek;
- statistiche verificate su Suricata EVE;
- report testuali e JSON;
- esclusione di IP grezzi e UID;
- correlazione bidirezionale con finestra temporale;
- 23 test automatici superati.

Sessione sovrapposta:

```text
Connessioni Zeek:                       35
Connessioni Zeek abbinate:              33
Eventi Suricata:                       318
Eventi Suricata correlati:             101
Copertura connessioni Zeek:          94,29%
Delta temporale medio:                0,027 s
Delta temporale massimo:              0,330 s
```

```text
Report pubblico: samples/09-python-log-analysis-report.md
Report privato:  reports/09-python-log-analysis-private.md
```

## Stato corrente

| Fase | Stato |
|---:|---|
| 1. Inventario | COMPLETATA |
| 2. Topologia | COMPLETATA |
| 3. Hotspot | COMPLETATA |
| 4. DHCP, routing e NAT | COMPLETATA |
| 5. Firewall nftables | COMPLETATA |
| 6. tcpdump | COMPLETATA |
| 7. Suricata | COMPLETATA |
| 8. Zeek | COMPLETATA |
| 9. Python | COMPLETATA |
| 10. Docker | PROSSIMA |
| 11. Test e hardening | DA FARE |

## Prossimi passi immediati

1. conservare il report privato come `reports/09-python-log-analysis-private.md`;
2. applicare permessi `600`;
3. verificare `git check-ignore` e `git status --short`;
4. sincronizzare il branch locale con il branch remoto;
5. passare a [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md);
6. definire schema, importazione idempotente e volumi persistenti;
7. montare log e report in sola lettura quando possibile.

## Report pubblici e privati

Nel repository pubblico restano guide, configurazioni parametrizzate, script commentati, report anonimizzati e campioni sintetici.

Nella cartella locale `reports/` restano output integrali, percorsi personali, porte effimere, query DNS, log operativi e report personali.

Non pubblicare password, token, MAC, PCAP, log integrali, query DNS personali, SNI TLS, certificati, valore di `digest_salt` o traffico di terzi.
