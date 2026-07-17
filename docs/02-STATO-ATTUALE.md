# Stato attuale del progetto

Ultimo aggiornamento operativo: 17 luglio 2026.

## Obiettivo principale

Costruire un gateway fisico Ubuntu nel quale:

- la scheda Wi-Fi interna MediaTek fornisce l'uscita Internet;
- la scheda Wi-Fi USB Realtek crea l'hotspot per i dispositivi di laboratorio;
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

Verificati:

- modalità AP sulla Realtek;
- SSID di laboratorio;
- client reali autenticati e associati;
- gateway `10.42.0.1`;
- raggiungibilità client → gateway;
- route Internet rimasta sulla MediaTek;
- arresto, eliminazione e ricreazione del profilo.

### Fase 4 — DHCP, routing e NAT

Completata e verificata il 16 luglio 2026.

Risultati:

- `ipv4.method=shared`;
- `dnsmasq` attivo per DHCP e DNS;
- sequenza `DHCPDISCOVER`, `DHCPOFFER`, `DHCPREQUEST`, `DHCPACK`;
- client con indirizzi `10.42.0.x`;
- `net.ipv4.ip_forward=1`;
- regole di forwarding automatiche osservate;
- masquerading per `10.42.0.0/24`;
- contatori NAT non nulli;
- traffico catturato sulla Realtek prima del NAT;
- traffico catturato sulla MediaTek dopo il NAT;
- DNS classico osservato in chiaro;
- TCP 443 e UDP 443 osservati senza contenuto applicativo leggibile;
- dati cellulari disabilitati durante la verifica del percorso;
- sicurezza Wi-Fi limitata a WPA2-RSN con CCMP/AES;
- spegnimento e riattivazione dell'hotspot verificati.

Report pubblico principale:

- [`../samples/04-dhcp-routing-nat-report.md`](../samples/04-dhcp-routing-nat-report.md).

Output pubblico supplementare:

- [`../samples/04-dhcp-routing-nat-output.md`](../samples/04-dhcp-routing-nat-output.md).

### Fase 5 — Firewall nftables

Completata e verificata il 17 luglio 2026.

Risultati:

- inventario delle porte in ascolto sul gateway;
- identificazione di `dnsmasq`, Avahi, CUPS e `wsdd`;
- filtro `INPUT` dedicato all'interfaccia hotspot;
- DHCP UDP 68→67 consentito;
- DNS TCP/UDP 53 verso `10.42.0.1` consentito;
- ICMP verso il gateway consentito;
- mDNS UDP 5353 e WS-Discovery UDP 3702 bloccati dall'hotspot;
- blocco finale degli altri accessi diretti a Ubuntu;
- test attivo del blocco TCP 631 verso il gateway;
- filtro `FORWARD` stateful tra hotspot e uplink;
- connessioni valide hotspot→Internet consentite;
- sole risposte `established,related` consentite verso i client;
- inoltri dall'hotspot verso la rete libvirt bloccati con test attivo;
- logging dei blocchi con rate limit;
- rollback e reload delle sole tabelle del progetto;
- coesistenza con NetworkManager, Docker e libvirt;
- script amministrativo protetto;
- servizio systemd dedicato;
- servizio abilitato all'avvio;
- persistenza verificata dopo riavvio reale.

Il servizio standard `nftables.service` resta `disabled/inactive` perché la configurazione standard contiene `flush ruleset`. Il progetto usa `security-gateway-firewall.service`, che modifica soltanto:

```text
security_gateway_input_filter
security_gateway_filter
```

Limiti dichiarati della verifica:

- non è stata generata attivamente una nuova connessione da un secondo host dell'uplink verso un client dell'hotspot;
- non è stato costruito appositamente traffico `ct state invalid`, anche se pochi pacchetti reali `invalid` sono stati osservati e bloccati.

Report pubblico principale:

- [`../samples/05-firewall-nftables-report.md`](../samples/05-firewall-nftables-report.md).

Non viene più usata una sottocartella `samples/reports/`: i report principali delle fasi sono direttamente nella radice di `samples/`.

## Percorso verificato

```text
Client 10.42.0.x
  -> Realtek 10.42.0.1
  -> filtro INPUT per DHCP/DNS/gateway
  -> filtro FORWARD stateful
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
| 4. DHCP, routing e NAT | COMPLETATA | DHCP, DNS, forwarding, NAT, catture prima/dopo e WPA2-RSN/CCMP verificati |
| 5. Firewall nftables | COMPLETATA | INPUT, FORWARD, log, rollback, systemd e persistenza verificati |
| 6. tcpdump | PROSSIMA | Approfondire filtri BPF, salvataggio, confronto e anonimizzazione |
| 7. Suricata | DA FARE | Non installato o configurato per questa topologia |
| 8. Zeek | DA FARE | Non installato o configurato per questa topologia |
| 9. Python | DA FARE | Nessun analizzatore dei log ancora sviluppato |
| 10. Docker dashboard | DA FARE | Nessuno stack definitivo |
| 11. Test e hardening | DA FARE | Include isolamento client, casi limite, backup e ripristino finale |

## Configurazione Wi-Fi verificata

```text
key-mgmt: wpa-psk
proto:    rsn
pairwise: ccmp
group:    ccmp
```

Il collegamento radio è protetto da WPA2-RSN/CCMP. Il traffico HTTPS/QUIC resta protetto a livello applicativo da TLS.

## Configurazione firewall persistente

Componenti installati sul gateway:

```text
/etc/security-gateway-firewall/security-gateway-input-filter.nft
/etc/security-gateway-firewall/security-gateway-filter.nft
/usr/local/sbin/security-gateway-firewall
/etc/systemd/system/security-gateway-firewall.service
```

Stato verificato dopo reboot:

```text
security-gateway-firewall.service: enabled / active (exited)
nftables.service standard:         disabled / inactive
INPUT:                              presente
FORWARD:                            presente
DHCP e DNS:                         funzionanti
navigazione:                        funzionante
```

L'hotspot resta ad avvio manuale perché `connection.autoconnect=no`.

## Materiale pubblico

Guide operative:

- [`steps/04-dhcp-routing-nat.md`](steps/04-dhcp-routing-nat.md);
- [`steps/05-firewall-nftables.md`](steps/05-firewall-nftables.md).

Report pubblici principali:

- [`../samples/04-dhcp-routing-nat-report.md`](../samples/04-dhcp-routing-nat-report.md);
- [`../samples/05-firewall-nftables-report.md`](../samples/05-firewall-nftables-report.md).

Configurazioni e script:

- [`../configs/nftables`](../configs/nftables);
- [`../scripts/security-gateway-firewall`](../scripts/security-gateway-firewall);
- [`../configs/systemd/security-gateway-firewall.service`](../configs/systemd/security-gateway-firewall.service).

## Vincoli di pubblicazione

Non pubblicare:

- password Wi-Fi;
- SSID domestici;
- MAC reali;
- nome completo `wlx...`;
- IP completo dell'host quando non necessario;
- PCAP grezzi;
- log integrali;
- screenshot originali non revisionati.

Gli output completi restano in `reports/`, esclusa da Git.

## Prossima azione

Passare alla fase 6:

```text
1. approfondire la sintassi dei filtri BPF
2. catturare quantità limitate di traffico autorizzato
3. distinguere hotspot, uplink e bridge virtuali
4. salvare PCAP con permessi e durata controllati
5. analizzare DNS, TCP, TLS e QUIC
6. documentare privacy e anonimizzazione
7. preparare dati revisionati per le fasi Suricata, Zeek e Python
```