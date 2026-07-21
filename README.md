# Ubuntu Security Gateway Lab

Laboratorio didattico per costruire un gateway di sicurezza su Ubuntu e imparare networking Linux, hotspot Wi-Fi, DHCP, routing, NAT, `nftables`, systemd, `tcpdump`, Suricata, Zeek, Python e servizi Docker.

> Usare il progetto esclusivamente su reti, sistemi e dispositivi propri o esplicitamente autorizzati.

## Architettura

```text
Dispositivo autorizzato
  -> Realtek USB hotspot
  -> Ubuntu gateway
     |-- DHCP e DNS locale
     |-- routing IPv4 e NAT
     |-- nftables INPUT/FORWARD
     |-- tcpdump
     |-- Suricata
     |-- Zeek
     |-- analisi Python
     `-- Docker per database e dashboard
  -> MediaTek uplink
  -> Internet
```

## Stato verificato

Le prime nove fasi sono completate:

| Fase | Stato |
|---:|---|
| 1. Inventario hardware e rete | COMPLETATA |
| 2. Topologia e indirizzamento | COMPLETATA |
| 3. Hotspot Realtek | COMPLETATA |
| 4. DHCP, routing e NAT | COMPLETATA |
| 5. Firewall nftables | COMPLETATA |
| 6. tcpdump | COMPLETATA |
| 7. Suricata | COMPLETATA |
| 8. Zeek | COMPLETATA |
| 9. Python | COMPLETATA |
| 10. Database e dashboard Docker | PROSSIMA |
| 11. Test e hardening | DA FARE |

## Risultati della fase 9

Sono stati realizzati:

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/tests/test_phase9.py
```

Funzionalità verificate:

- lettura streaming di JSON Lines e gzip;
- analisi dei log `conn.log` Zeek;
- analisi di Suricata `eve.json`;
- report testuali e JSON;
- esclusione di IP grezzi e UID dai report;
- correlazione bidirezionale tramite 5-tupla e timestamp;
- 23 test automatici superati.

Nella sessione con entrambi i sensori attivi, 33 delle 35 connessioni Zeek hanno trovato almeno un evento Suricata compatibile. Il delta temporale medio era 0,027 secondi.

## Documentazione

1. [Obiettivi e architettura](docs/OBIETTIVI_E_PROGETTO.md)
2. [Stato attuale](docs/02-STATO-ATTUALE.md)
3. [Roadmap](docs/00-ROADMAP.md)
4. [Indice documentazione](docs/README.md)
5. [Guide operative](docs/steps)

Guide recenti:

- [`docs/steps/07-suricata.md`](docs/steps/07-suricata.md)
- [`docs/steps/08-zeek.md`](docs/steps/08-zeek.md)
- [`docs/steps/09-python-log-analysis.md`](docs/steps/09-python-log-analysis.md)

## Report pubblici

```text
samples/07-suricata-report.md
samples/08-zeek-report.md
samples/09-python-log-analysis-report.md
```

## Report privati

`reports/` è esclusa tramite `.gitignore` e contiene output integrali, percorsi locali e report personali.

```text
reports/07-suricata-private.md
reports/08-zeek-private.md
reports/09-python-log-analysis-private.md
```

I PCAP, `eve.json`, i log Zeek integrali, query DNS, SNI TLS e altri dati grezzi non vengono pubblicati.

## Esecuzione dei test Python

```bash
cd python
python3 -m unittest discover -s tests -v
```

Risultato verificato:

```text
Ran 23 tests

OK
```

## Modalità operativa dei sensori

Suricata e Zeek sono usati su richiesta durante il laboratorio:

```bash
sudo systemctl start suricata
sudo systemctl stop suricata

sudo /opt/zeek/bin/zeekctl deploy
sudo /opt/zeek/bin/zeekctl stop
```

## Struttura

```text
.
|-- README.md
|-- docs/
|-- configs/
|-- scripts/
|-- python/
|-- docker/
|-- samples/
`-- reports/      privato e ignorato da Git
```

## Privacy

Non pubblicare password Wi-Fi, token, MAC, nomi completi delle interfacce, hostname o percorsi personali, IP non necessari, query DNS, PCAP grezzi, log integrali, SNI TLS, certificati o traffico appartenente a terzi.

## Licenza

MIT.
