# Stato attuale del progetto

Ultimo aggiornamento operativo: 20 luglio 2026.

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

Piano verificato:

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
- TCP 443 e UDP 443 senza contenuto applicativo leggibile;
- dati cellulari disabilitati durante la verifica;
- WPA2-RSN con CCMP/AES;
- spegnimento e riattivazione dell’hotspot.

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

Guida:

- [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md).

Report pubblico:

- [`../samples/06-cattura-tcpdump-report.md`](../samples/06-cattura-tcpdump-report.md).

Report privato locale:

```text
reports/06-cattura-tcpdump-private.md
```

### Fase 7 — Suricata IDS

Completata e verificata il 20 luglio 2026.

Risultati:

- Suricata 8.0.3 installato sull’host Ubuntu, non in Docker;
- `suricata-update` 1.3.7 e `jq` 1.8.1 installati;
- supporto AF_PACKET e Hyperscan verificato;
- errore iniziale causato da `eth0` inesistente diagnosticato;
- `HOME_NET` impostato a `10.42.0.0/24`;
- interfaccia hotspot configurata per AF_PACKET;
- oltre 52.000 regole caricate senza errori;
- test della configurazione con codice `0`;
- eventi flow, QUIC, mDNS, DNS, TLS, HTTP, fileinfo e DHCP osservati;
- alert decoder `SURICATA Ethertype unknown` documentato senza interpretarlo come prova di attacco;
- servizio avviato su richiesta con stato `active/disabled`;
- arresto verificato con stato `inactive/disabled`;
- regola locale ICMP innocua con SID `1000001`;
- alert `LAB Suricata ICMP test` prodotto con azione `allowed`;
- prova di circa 62 secondi con drop finali dello `0,25%`;
- `eve.json`, `fast.log`, `stats.log` e `suricata.log` letti;
- controllo giornaliero logrotate con soglia di 1 MiB;
- 14 rotazioni compresse previste;
- rotazione reale di `eve.json` in `eve.json.1.gz`;
- Suricata mantenuto disabilitato al boot.

Guida:

- [`steps/07-suricata.md`](steps/07-suricata.md).

Report pubblico:

- [`../samples/07-suricata-report.md`](../samples/07-suricata-report.md).

Report privato locale:

```text
reports/07-suricata-private.md
```

Il report privato e i log integrali non devono essere aggiunti a Git.

## Percorso verificato

```text
Client 10.42.0.x
  -> Realtek 10.42.0.1
  -> nftables INPUT/FORWARD
  -> Suricata AF_PACKET in modalità IDS passiva
  -> NAT/masquerading NetworkManager
  -> MediaTek 192.168.10.x
  -> router 192.168.10.1
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
| 7. Suricata | COMPLETATA | IDS passivo, regole, alert controllato, systemd on demand e logrotate verificati |
| 8. Zeek | PROSSIMA | Installazione e log di rete strutturati |
| 9. Python | DA FARE | Nessun analizzatore dei log ancora sviluppato |
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
hotspot:                            avvio manuale
```

Comandi Suricata:

```bash
sudo systemctl start suricata
sudo systemctl stop suricata
```

## Materiale pubblico

Guide più recenti:

- [`steps/05-firewall-nftables.md`](steps/05-firewall-nftables.md);
- [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md);
- [`steps/07-suricata.md`](steps/07-suricata.md).

Report principali:

- [`../samples/05-firewall-nftables-report.md`](../samples/05-firewall-nftables-report.md);
- [`../samples/06-cattura-tcpdump-report.md`](../samples/06-cattura-tcpdump-report.md);
- [`../samples/07-suricata-report.md`](../samples/07-suricata-report.md).

## Vincoli di pubblicazione

Non pubblicare password Wi-Fi, SSID domestici, MAC reali, nome completo `wlx...`, hostname o percorsi personali, IP e porte completi non necessari, PCAP grezzi, query DNS personali, log integrali o file `eve.json` completi.

Gli output completi restano in `reports/`, esclusa da Git. I PCAP restano in directory private esterne al repository.

## Prossima azione

Passare alla fase 8: installare Zeek sull’host Ubuntu, produrre log strutturati e confrontarli con gli eventi Suricata.
