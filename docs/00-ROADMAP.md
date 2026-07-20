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
| 8 | [`steps/08-zeek.md`](steps/08-zeek.md) | Generare log di rete strutturati | PROSSIMO |
| 9 | [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md) | Leggere log e produrre statistiche | DA FARE |
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

- backup del ruleset;
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

Sono stati verificati:

- sintassi dei filtri BPF;
- catture limitate al client autorizzato;
- interpretazione di indirizzi, porte e direzioni;
- UDP/443 compatibile con QUIC/HTTP/3;
- consultazione WHOIS e limiti di attribuzione;
- DNS tradizionale con record `A`, `AAAA`, `CNAME` e `HTTPS`;
- richieste ICMP senza risposta del telefono;
- handshake TCP completo;
- flag ACK, PSH, FIN e RST;
- traffico cifrato senza decifrazione;
- stesso flusso abbinato riga per riga prima e dopo il NAT;
- traduzione inversa e decremento TTL;
- PCAP privato di 20 record con snapshot di 128 byte;
- formato Linux cooked v2;
- permessi `600`;
- creazione e lettura compatibili con AppArmor attivo;
- nessun PCAP grezzo pubblicato;
- nessuna perdita segnalata dal kernel.

Report pubblico principale:

```text
samples/06-cattura-tcpdump-report.md
```

Report privato locale:

```text
reports/06-cattura-tcpdump-private.md
```

Il report privato e il PCAP restano fuori da Git.

## Fase 7 — Suricata

Completata e verificata il 20 luglio 2026.

Sono stati verificati:

- installazione sull’host Ubuntu e non in Docker;
- Suricata 8.0.3, `suricata-update` e `jq`;
- supporto AF_PACKET e Hyperscan;
- diagnosi dell’interfaccia predefinita `eth0` inesistente;
- `HOME_NET` limitato a `10.42.0.0/24`;
- interfaccia hotspot configurata in AF_PACKET;
- oltre 52.000 regole caricate senza errori;
- test della configurazione con codice di uscita `0`;
- eventi flow, DNS, TLS, QUIC, HTTP, DHCP, mDNS e fileinfo;
- servizio avviato su richiesta con stato `active/disabled`;
- arresto con stato `inactive/disabled`;
- regola locale ICMP innocua con SID `1000001`;
- alert controllato con azione `allowed`;
- statistiche AF_PACKET e drop finali dello `0,25%`;
- rotazione giornaliera controllata da timer e soglia di 1 MiB;
- 14 archivi compressi previsti;
- rotazione reale di `eve.json` in `eve.json.1.gz`.

Report pubblico:

```text
samples/07-suricata-report.md
```

Report privato locale:

```text
reports/07-suricata-private.md
```

Suricata resta disabilitato al boot e viene avviato soltanto durante le sessioni di laboratorio.

## Fase 8 — Zeek

- installazione e configurazione sull’host Ubuntu;
- scelta dell’interfaccia di osservazione;
- analisi di `conn.log`, `dns.log`, `http.log`, `ssl.log` e `notice.log`;
- formato TSV o JSON;
- confronto con `eve.json` di Suricata;
- rotazione e conservazione;
- uso su richiesta senza avvio automatico non necessario.

## Fase 9 — Python

Percorso progressivo:

1. leggere file;
2. gestire righe e colonne;
3. usare funzioni, dizionari e contatori;
4. leggere JSON Suricata;
5. leggere log Zeek;
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
