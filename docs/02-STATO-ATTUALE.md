# Stato attuale del progetto

Ultimo aggiornamento operativo: 18 luglio 2026.

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

- inventario delle porte in ascolto;
- filtro `INPUT` dedicato all’hotspot;
- DHCP e DNS consentiti;
- ICMP verso il gateway consentito;
- mDNS e WS-Discovery bloccati;
- altri accessi diretti a Ubuntu bloccati;
- test TCP 631 verso il gateway;
- filtro `FORWARD` stateful;
- traffico valido hotspot→Internet consentito;
- sole risposte `established,related` consentite verso i client;
- rete privata libvirt bloccata dall’hotspot con test attivo;
- logging con rate limit;
- rollback e reload delle sole tabelle del progetto;
- coesistenza con NetworkManager, Docker e libvirt;
- script amministrativo e servizio systemd dedicato;
- persistenza verificata dopo riavvio reale.

Il progetto usa `security-gateway-firewall.service`. Il servizio standard `nftables.service` resta disabilitato perché la configurazione standard contiene `flush ruleset`.

Report:

- [`../samples/05-firewall-nftables-report.md`](../samples/05-firewall-nftables-report.md).

### Fase 6 — Cattura tcpdump

Completata e verificata il 18 luglio 2026.

Risultati:

- `tcpdump`, libpcap e OpenSSL verificati;
- filtri BPF applicati a un solo client autorizzato;
- IP, porte e direzioni interpretati;
- traffico UDP/443 compatibile con QUIC/HTTP/3;
- WHOIS usato con limiti di attribuzione dichiarati;
- DNS tradizionale osservato con record `A`, `AAAA`, `CNAME` e `HTTPS`;
- tre richieste ICMP trasmesse, senza risposta del telefono;
- handshake TCP completo SYN, SYN-ACK e ACK;
- flag ACK, PSH, FIN e RST riconosciuti;
- dati TCP/443 riconosciuti come cifrati senza decifrarli;
- stesso flusso UDP/443 osservato simultaneamente prima e dopo il NAT;
- traduzione inversa delle risposte verificata;
- decremento TTL durante il forwarding verificato;
- traffico inoltrato distinto dal traffico locale del gateway;
- PCAP privato limitato a 20 record e snapshot di 128 byte;
- formato PCAP 2.4 Linux cooked v2 verificato;
- permessi finali `600`;
- profilo AppArmor `tcpdump` mantenuto attivo;
- creazione e lettura completate tramite standard output/input;
- nessun PCAP grezzo pubblicato;
- nessun pacchetto perso dal kernel nelle catture documentate.

Guida:

- [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md).

Unico report pubblico principale:

- [`../samples/06-cattura-tcpdump-report.md`](../samples/06-cattura-tcpdump-report.md).

Report privato locale previsto:

```text
reports/06-cattura-tcpdump-private.md
```

Il report privato e il PCAP non devono essere aggiunti a Git.

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

La fase 6 ha abbinato riga per riga lo stesso flusso sui due lati:

```text
wlx<REDACTED> In  10.42.0.x:PORTA    -> IP_REMOTO:443
wlp13s0 Out       192.168.10.x:PORTA -> IP_REMOTO:443

wlp13s0 In        IP_REMOTO:443 -> 192.168.10.x:PORTA
wlx<REDACTED> Out IP_REMOTO:443 -> 10.42.0.x:PORTA
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
| 7. Suricata | PROSSIMA | Installazione e configurazione iniziale in modalità passiva IDS |
| 8. Zeek | DA FARE | Non installato o configurato per questa topologia |
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

## Configurazione firewall persistente

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

L’hotspot resta ad avvio manuale perché `connection.autoconnect=no`.

## Materiale pubblico

Guide più recenti:

- [`steps/04-dhcp-routing-nat.md`](steps/04-dhcp-routing-nat.md);
- [`steps/05-firewall-nftables.md`](steps/05-firewall-nftables.md);
- [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md).

Report principali:

- [`../samples/04-dhcp-routing-nat-report.md`](../samples/04-dhcp-routing-nat-report.md);
- [`../samples/05-firewall-nftables-report.md`](../samples/05-firewall-nftables-report.md);
- [`../samples/06-cattura-tcpdump-report.md`](../samples/06-cattura-tcpdump-report.md).

## Vincoli di pubblicazione

Non pubblicare password Wi-Fi, SSID domestici, MAC reali, nome completo `wlx...`, hostname o percorsi personali, IP e porte completi non necessari, PCAP grezzi, query DNS personali, log integrali o screenshot originali.

Gli output completi restano in `reports/`, esclusa da Git. I PCAP restano in directory private esterne al repository.

## Prossima azione

Passare alla fase 7 soltanto dopo aver copiato il report privato della fase 6 in `reports/` e verificato che sia ignorato da Git. La fase 7 installerà Suricata inizialmente in modalità passiva IDS, senza bloccare traffico.