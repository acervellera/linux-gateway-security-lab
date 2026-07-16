# Stato attuale del progetto

Ultimo aggiornamento operativo: 16 luglio 2026.

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

La subnet non si sovrappone alla rete domestica o alle reti Docker.

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
- avviso iOS relativo a WPA/WPA2-TKIP eliminato;
- spegnimento e riattivazione dell'hotspot verificati.

Percorso verificato:

```text
Client 10.42.0.x
  -> Realtek 10.42.0.1
  -> forwarding IPv4
  -> NAT/masquerading
  -> MediaTek 192.168.10.x
  -> router 192.168.10.1
  -> Internet
```

La cattura prima del NAT mostra `10.42.0.x` come sorgente; quella dopo il NAT mostra `192.168.10.x`.

## Stato delle fasi

| Fase | Stato | Nota |
|---:|---|---|
| 1. Inventario hardware e rete | COMPLETATA | Hardware, driver, route, rfkill e modalità AP verificati |
| 2. Topologia e indirizzamento | COMPLETATA | Subnet e percorso definiti senza conflitti |
| 3. Hotspot Realtek | COMPLETATA | Hotspot, client, gateway e rollback verificati |
| 4. DHCP, routing e NAT | COMPLETATA | DHCP, DNS, forwarding, NAT, catture prima/dopo e WPA2-RSN/CCMP verificati |
| 5. Firewall nftables | PROSSIMA | Preparare ruleset stateful e rollback sicuro |
| 6. tcpdump | DA FARE | La fase 4 ha usato tcpdump per il NAT; la fase 6 approfondirà filtri, salvataggio e analisi |
| 7. Suricata | DA FARE | Non installato o configurato per questa topologia |
| 8. Zeek | DA FARE | Non installato o configurato per questa topologia |
| 9. Python | DA FARE | Nessun analizzatore dei log ancora sviluppato |
| 10. Docker dashboard | DA FARE | Nessuno stack definitivo |
| 11. Test e hardening | DA FARE | Include persistenza, uplink assente, isolamento e ripristino finale |

## Configurazione Wi-Fi verificata

```text
key-mgmt: wpa-psk
proto:    rsn
pairwise: ccmp
group:    ccmp
```

Il collegamento radio è protetto da WPA2-RSN/CCMP. Il traffico HTTPS/QUIC resta protetto a livello applicativo da TLS.

## Modifiche applicate

Sono stati:

- mantenuti `ipv4.method=shared` e `10.42.0.1/24`;
- osservati DHCP, DNS, forwarding e NAT automatici di NetworkManager;
- limitati protocollo e cifrari Wi-Fi a RSN/CCMP;
- disattivato e riattivato il profilo per applicare e verificare la modifica.

Non sono ancora stati:

- applicati ruleset definitivi `nftables`;
- limitato esplicitamente l'accesso dei client alla rete domestica;
- verificato l'isolamento tra client;
- separati DHCP e DNS dagli automatismi di NetworkManager;
- installati o configurati Suricata e Zeek;
- verificati persistenza e comportamento finale dopo riavvio.

## Materiale pubblico

- [`steps/04-dhcp-routing-nat.md`](steps/04-dhcp-routing-nat.md);
- [`../samples/04-dhcp-routing-nat-report.md`](../samples/04-dhcp-routing-nat-report.md);
- [`../samples/04-dhcp-routing-nat-output.md`](../samples/04-dhcp-routing-nat-output.md);
- immagini revisionate prima/dopo la correzione Wi-Fi in `images/`.

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

Passare alla fase 5:

```text
1. salvare lo stato firewall corrente
2. definire policy e catene stateful
3. consentire established,related
4. limitare inoltro hotspot -> uplink
5. proteggere il gateway e la rete domestica
6. predisporre rollback sicuro
7. verificare client, DNS e Internet
```
