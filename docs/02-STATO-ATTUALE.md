# Stato attuale del progetto

Ultimo aggiornamento operativo: 21 luglio 2026.

## Obiettivo principale

Costruire un gateway fisico Ubuntu nel quale:

- la scheda Wi-Fi interna MediaTek fornisce l’uscita Internet;
- la scheda Wi-Fi USB Realtek crea l’hotspot per i dispositivi di laboratorio;
- Ubuntu esegue routing, firewall, NAT e monitoraggio;
- Suricata e Zeek producono eventi e log;
- Python analizza i log;
- Docker ospita database e dashboard senza gestire direttamente il routing principale.

## Fasi completate

### Fase 1 — Inventario hardware e rete

Verificati sistema, kernel, MediaTek, Realtek, driver, supporto AP, route, rfkill e reti Docker esistenti.

### Fase 2 — Topologia e indirizzamento

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
DNS_SERVER=10.42.0.1
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
```

La subnet non si sovrappone alla rete domestica o alle reti Docker osservate.

### Fase 3 — Hotspot Realtek

Verificati modalità AP, client reali autenticati, gateway `10.42.0.1`, raggiungibilità client→gateway, uplink mantenuto sulla MediaTek e rollback del profilo.

### Fase 4 — DHCP, routing e NAT

Completata il 16 luglio 2026.

Risultati:

- `ipv4.method=shared`;
- `dnsmasq` per DHCP e DNS;
- sequenza DHCP completa;
- client con indirizzi `10.42.0.x`;
- `net.ipv4.ip_forward=1`;
- forwarding e masquerading osservati;
- traffico prima e dopo il NAT;
- DNS classico in chiaro;
- TCP 443 e UDP 443;
- dati cellulari disabilitati durante la verifica;
- WPA2-RSN con CCMP/AES.

Report:

- [`../samples/04-dhcp-routing-nat-report.md`](../samples/04-dhcp-routing-nat-report.md);
- [`../samples/04-dhcp-routing-nat-output.md`](../samples/04-dhcp-routing-nat-output.md).

### Fase 5 — Firewall nftables

Completata il 17 luglio 2026.

Risultati:

- filtro `INPUT` dedicato all’hotspot;
- DHCP, DNS e ICMP necessari consentiti;
- mDNS, WS-Discovery e accessi non previsti bloccati;
- filtro `FORWARD` stateful;
- traffico valido hotspot→Internet consentito;
- sole risposte `established,related` consentite verso i client;
- rete privata libvirt bloccata dall’hotspot;
- logging con rate limit;
- rollback e reload delle sole tabelle del progetto;
- coesistenza con NetworkManager, Docker e libvirt;
- script amministrativo e servizio systemd dedicato;
- persistenza verificata dopo riavvio reale.

Report:

- [`../samples/05-firewall-nftables-report.md`](../samples/05-firewall-nftables-report.md).

### Fase 6 — Cattura tcpdump

Completata e verificata il 18 luglio 2026.

Risultati:

- filtri BPF applicati a un client autorizzato;
- DNS tradizionale con record `A`, `AAAA`, `CNAME` e `HTTPS`;
- richieste ICMP;
- handshake TCP completo e principali flag;
- traffico cifrato riconosciuto senza decifrazione;
- stesso flusso osservato prima e dopo il NAT;
- traduzione inversa e decremento TTL;
- PCAP privato limitato a 20 record e snapshot di 128 byte;
- formato Linux cooked v2 e permessi `600`;
- AppArmor mantenuto attivo;
- nessun PCAP grezzo pubblicato.

```text
Guida:           docs/steps/06-cattura-tcpdump.md
Report pubblico: samples/06-cattura-tcpdump-report.md
Report privato:  reports/06-cattura-tcpdump-private.md
```

### Fase 7 — Suricata IDS

Completata e verificata il 20 luglio 2026.

Risultati:

- Suricata 8.0.3 installato sull’host Ubuntu;
- `suricata-update` 1.3.7 e `jq` 1.8.1;
- supporto AF_PACKET e Hyperscan;
- errore iniziale causato da `eth0` inesistente diagnosticato;
- `HOME_NET` impostato a `10.42.0.0/24`;
- oltre 52.000 regole caricate senza errori;
- eventi flow, QUIC, mDNS, DNS, TLS, HTTP, fileinfo e DHCP;
- alert decoder documentato senza interpretarlo come prova di attacco;
- servizio avviato su richiesta e disabilitato al boot;
- regola ICMP locale con alert `allowed`;
- prova gestita con drop finali dello `0,25%`;
- rotazione reale di `eve.json` in `eve.json.1.gz`.

```text
Guida:           docs/steps/07-suricata.md
Report pubblico: samples/07-suricata-report.md
Report privato:  reports/07-suricata-private.md
```

### Fase 8 — Zeek e log di rete

Completata e verificata il 21 luglio 2026.

Risultati:

- Zeek 8.0.9 e ZeekControl installati sotto `/opt/zeek`;
- plugin AF_PACKET e Pcap verificati;
- nodo standalone configurato sull’interfaccia hotspot;
- `networks.cfg` limitato a `10.42.0.0/24`;
- `PrivateAddressSpaceIsLocal = 0`;
- `digest_salt` personalizzato senza pubblicarne il valore;
- log JSON abilitati;
- cattura manuale di 12.850 pacchetti;
- zero pacchetti persi dal kernel;
- zero gap TCP e zero byte mancanti;
- log `conn`, `dns`, `ssl` e `quic` osservati;
- controllo `zeekctl check` completato;
- avvio e arresto gestiti tramite ZeekControl;
- archiviazione dei log all’arresto;
- Suricata ripristinato e attivo al termine.

Prova gestita:

```text
conn.log    19 eventi
dns.log     85 eventi
ssl.log     13 eventi
quic.log    13 eventi
```

Tutti i file controllati erano JSON validi.

La rotazione oraria è configurata ma non è stata osservata per un’ora completa. È stata verificata l’archiviazione gestita all’arresto e la lettura dei file compressi.

```text
Guida:           docs/steps/08-zeek.md
Report pubblico: samples/08-zeek-report.md
Report privato:  reports/08-zeek-private.md
```

Il report privato e i log integrali non devono essere aggiunti a Git.

## Percorso verificato

```text
Client 10.42.0.x
  -> Realtek 10.42.0.1
  -> nftables INPUT/FORWARD
  -> Suricata IDS passivo oppure Zeek standalone
  -> NAT/masquerading NetworkManager
  -> MediaTek 192.168.10.x
  -> router
  -> Internet
```

## Stato delle fasi

| Fase | Stato | Nota |
|---:|---|---|
| 1. Inventario hardware e rete | COMPLETATA | Hardware, driver, route, rfkill e modalità AP verificati |
| 2. Topologia e indirizzamento | COMPLETATA | Subnet e percorso definiti senza conflitti |
| 3. Hotspot Realtek | COMPLETATA | Hotspot, client, gateway e rollback verificati |
| 4. DHCP, routing e NAT | COMPLETATA | DHCP, DNS, forwarding, NAT e WPA2-RSN/CCMP verificati |
| 5. Firewall nftables | COMPLETATA | INPUT, FORWARD, log, rollback, systemd e persistenza verificati |
| 6. tcpdump | COMPLETATA | DNS, ICMP, handshake TCP, NAT, PCAP e AppArmor verificati |
| 7. Suricata | COMPLETATA | IDS passivo, regole, alert controllato e logrotate verificati |
| 8. Zeek | COMPLETATA | Log JSON DNS/TLS/QUIC, ZeekControl e archiviazione verificati |
| 9. Python | PROSSIMA | Primo analizzatore dei log da sviluppare |
| 10. Docker dashboard | DA FARE | Nessuno stack definitivo |
| 11. Test e hardening | DA FARE | Isolamento client, casi limite, backup e ripristino finale |

## Configurazione Wi-Fi verificata

```text
key-mgmt: wpa-psk
proto:    rsn
pairwise: ccmp
group:    ccmp
```

Il collegamento radio è protetto da WPA2-RSN/CCMP. Il traffico HTTPS/QUIC resta protetto da TLS a livello applicativo.

## Servizi e modalità operative

```text
security-gateway-firewall.service: enabled / active (exited)
nftables.service standard:         disabled / inactive
Suricata al boot:                   disabled
Suricata durante il laboratorio:    start/stop manuale
Zeek al boot:                       non configurato
Zeek durante il laboratorio:        deploy/stop manuale
hotspot:                            avvio manuale
```

Comandi principali:

```bash
sudo systemctl start suricata
sudo systemctl stop suricata

sudo /opt/zeek/bin/zeekctl deploy
sudo /opt/zeek/bin/zeekctl stop
```

## Materiale pubblico

Guide più recenti:

- [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md);
- [`steps/07-suricata.md`](steps/07-suricata.md);
- [`steps/08-zeek.md`](steps/08-zeek.md).

Report principali:

- [`../samples/06-cattura-tcpdump-report.md`](../samples/06-cattura-tcpdump-report.md);
- [`../samples/07-suricata-report.md`](../samples/07-suricata-report.md);
- [`../samples/08-zeek-report.md`](../samples/08-zeek-report.md).

## Vincoli di pubblicazione

Non pubblicare password Wi-Fi, SSID domestici, MAC reali, nome completo `wlx...`, hostname o percorsi personali, IP e porte completi non necessari, PCAP grezzi, query DNS personali, log integrali, file `eve.json` completi, log Zeek integrali, SNI TLS, certificati o valore di `digest_salt`.

Gli output completi restano in `reports/`, esclusa da Git. I PCAP restano in directory private esterne al repository.

## Prossima azione

Passare alla fase 9: scrivere il primo programma Python commentato che legge i log JSON di Zeek senza modificare la rete.
