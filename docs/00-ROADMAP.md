# Roadmap completa

## Obiettivo generale

Costruire un gateway Ubuntu attraverso cui far passare il traffico di dispositivi autorizzati, osservarlo in modo difensivo e analizzarne i log con Python.

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
| 9 | [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md) | Leggere log e produrre statistiche | PROSSIMO |
| 10 | [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md) | Salvare e visualizzare dati | DA FARE |
| 11 | [`steps/11-test-hardening-backup.md`](steps/11-test-hardening-backup.md) | Test finali, hardening, backup e ripristino | DA FARE |

## Fase 1 — Inventario

Verificati Ubuntu, kernel, interfacce, driver MediaTek e Realtek, modalità AP, route predefinita, NetworkManager, rfkill e reti Docker.

## Fase 2 — Topologia

Piano verificato:

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
DNS_SERVER=10.42.0.1
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
```

## Fase 3 — Hotspot Realtek

Completata il 15 luglio 2026. Verificati modalità AP, `10.42.0.1/24`, `ipv4.method=shared`, client reali, route MediaTek e rollback del profilo.

## Fase 4 — DHCP, routing e NAT

Completata il 16 luglio 2026.

Verificati:

- DHCP e DNS tramite `dnsmasq`;
- sequenza DHCP completa;
- `net.ipv4.ip_forward=1`;
- forwarding e masquerading;
- traffico sui due lati del NAT;
- DNS classico;
- TCP 443 e UDP 443;
- assenza di percorso cellulare durante il test;
- WPA2-RSN con CCMP/AES.

Percorso:

```text
client 10.42.0.x
  -> Realtek 10.42.0.1
  -> forwarding
  -> NAT/masquerading
  -> MediaTek 192.168.10.x
  -> router
  -> Internet
```

## Fase 5 — Firewall nftables

Completata il 17 luglio 2026.

Realizzati e provati:

- filtro `INPUT` sull’hotspot;
- filtro `FORWARD` stateful;
- DHCP, DNS e ICMP necessari consentiti;
- mDNS, WS-Discovery e accessi non previsti bloccati;
- test TCP 631;
- test hotspot→rete libvirt;
- logging con rate limit;
- rollback delle sole tabelle del progetto;
- coesistenza con NetworkManager, Docker e libvirt;
- script amministrativo;
- servizio systemd dedicato;
- persistenza dopo reboot reale.

Componenti pubblici:

```text
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
samples/05-firewall-nftables-report.md
```

## Fase 6 — tcpdump

Completata e verificata il 18 luglio 2026.

Sono stati verificati filtri BPF, DNS tradizionale, ICMP, handshake TCP, traffico cifrato, confronto prima e dopo il NAT, decremento TTL, PCAP privato limitato, AppArmor attivo e assenza di perdite segnalate dal kernel.

```text
Report pubblico: samples/06-cattura-tcpdump-report.md
Report privato:  reports/06-cattura-tcpdump-private.md
```

## Fase 7 — Suricata

Completata e verificata il 20 luglio 2026.

Sono stati verificati:

- Suricata 8.0.3 sull’host Ubuntu;
- supporto AF_PACKET e Hyperscan;
- `HOME_NET` limitato a `10.42.0.0/24`;
- oltre 52.000 regole caricate senza errori;
- eventi flow, DNS, TLS, QUIC, HTTP, DHCP, mDNS e fileinfo;
- servizio avviato su richiesta e disabilitato al boot;
- regola ICMP locale con alert `allowed`;
- drop finali dello `0,25%` nella prova gestita;
- rotazione reale di `eve.json` in archivio gzip.

```text
Report pubblico: samples/07-suricata-report.md
Report privato:  reports/07-suricata-private.md
```

## Fase 8 — Zeek

Completata e verificata il 21 luglio 2026.

Sono stati verificati:

- Zeek 8.0.9 e ZeekControl installati sotto `/opt/zeek`;
- plugin AF_PACKET e Pcap;
- nodo standalone sull’interfaccia hotspot;
- rete locale `10.42.0.0/24`;
- `PrivateAddressSpaceIsLocal = 0`;
- `digest_salt` personalizzato;
- formato JSON tramite `policy/tuning/json-logs`;
- cattura manuale di 12.850 pacchetti con zero drop kernel;
- zero gap TCP e zero byte mancanti;
- log `conn`, `dns`, `ssl` e `quic`;
- avvio e arresto tramite ZeekControl;
- archiviazione dei log all’arresto;
- ripristino finale di Suricata.

Conteggi della prova gestita:

```text
conn.log    19 eventi
dns.log     85 eventi
ssl.log     13 eventi
quic.log    13 eventi
```

Tutti i file controllati erano JSON validi.

La rotazione è configurata ogni ora; non è stata attesa un’ora completa. È stata verificata l’archiviazione gestita all’arresto e la lettura dei file `.log.gz`.

```text
Guida:           docs/steps/08-zeek.md
Report pubblico: samples/08-zeek-report.md
Report privato:  reports/08-zeek-private.md
```

Zeek resta spento durante il normale funzionamento e viene avviato manualmente durante il laboratorio.

## Fase 9 — Python

Percorso progressivo:

1. leggere file;
2. gestire righe e oggetti JSON;
3. usare funzioni, dizionari e contatori;
4. leggere `eve.json` di Suricata;
5. leggere log JSON di Zeek;
6. calcolare IP, domini e porte frequenti;
7. raggruppare per dispositivo e tempo;
8. esportare CSV e JSON;
9. aggiungere error handling e logging;
10. creare test.

Ogni libreria, funzione e blocco di codice verrà commentato e spiegato.

## Fase 10 — Docker

Docker verrà usato per servizi applicativi: importazione, database, dashboard, volumi e accesso ai log in sola lettura. Nessun container privilegiato senza necessità dimostrata.

## Fase 11 — Test e hardening

- uplink assente;
- isolamento tra client;
- test da un secondo host dell’uplink;
- casi `ct state invalid` controllati;
- accessi consentiti tra reti;
- IDS fermo;
- spazio e rotazione log;
- backup e ripristino;
- rimozione sicura del laboratorio.

## Criterio di completamento del progetto

Il progetto è completato quando un dispositivo autorizzato:

1. si collega all’hotspot;
2. riceve configurazione IP corretta;
3. usa Ubuntu come unico gateway;
4. raggiunge Internet tramite MediaTek;
5. è filtrato da nftables;
6. genera log Suricata e Zeek;
7. compare nei report Python;
8. compare nella dashboard Docker;
9. continua a funzionare dopo test controllati;
10. può essere disconnesso e ripristinato con procedure documentate.
