# Lavoro svolto e prossimi passi

## Funzione del documento

Questo file riassume l’evoluzione reale del gateway fisico Ubuntu. Per lo stato più aggiornato usare [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md); per comandi e rollback usare le guide in [`steps`](steps).

## Gateway fisico

```text
Telefono / dispositivo autorizzato
  -> SecurityGatewayLab
  -> Realtek USB AP
  -> Ubuntu gateway
  -> nftables INPUT e FORWARD
  -> Suricata AF_PACKET in modalità IDS passiva
  -> NAT/masquerading
  -> MediaTek wlp13s0
  -> router
  -> Internet
```

## Fase 1 completata — Inventario

Verificati Ubuntu, kernel, schede MediaTek e Realtek, driver, supporto AP, route predefinita, rfkill e reti Docker.

## Fase 2 completata — Topologia

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
```

## Fase 3 completata — Hotspot

Realtek in modalità AP, client reali associati, indirizzi `10.42.0.x`, gateway raggiunto, Internet tramite MediaTek e rollback del profilo verificato.

## Fase 4 completata — DHCP, routing e NAT

Completata il 16 luglio 2026.

Verificati `dnsmasq`, sequenza DHCP, forwarding IPv4, masquerading, traffico sui lati Realtek e MediaTek, DNS classico, TCP/443, UDP/443 e WPA2-RSN con CCMP/AES.

```text
10.42.0.x:porta -> NAT -> 192.168.10.x:porta -> server:443
```

## Fase 5 completata — Firewall nftables

Completata il 17 luglio 2026.

### INPUT

Consentiti DHCP, DNS e ICMP necessari. Bloccati mDNS, WS-Discovery e accessi non previsti al gateway. Testato il blocco TCP 631.

### FORWARD

```text
hotspot -> uplink, new/established/related  ACCEPT
uplink -> hotspot, established/related      ACCEPT
uplink -> hotspot, new                      LOG + DROP
hotspot -> altre interfacce                 LOG + DROP
altre interfacce -> hotspot                 LOG + DROP
invalid sul percorso controllato            DROP
```

Testato il blocco hotspot→rete libvirt. Internet è rimasto funzionante.

### Persistenza

Installati script, configurazioni e servizio `security-gateway-firewall.service`. Persistenza verificata dopo riavvio reale. Il servizio standard `nftables.service` resta disabilitato.

## Fase 6 completata — tcpdump

Completata e verificata il 18 luglio 2026.

Sono stati verificati:

- filtri BPF limitati;
- DNS con record `A`, `AAAA`, `CNAME` e `HTTPS`;
- richieste ICMP;
- handshake TCP completo;
- flag ACK, PSH, FIN e RST;
- traffico cifrato;
- NAT riga per riga sui due lati;
- decremento TTL;
- PCAP privato di 20 record e snapshot 128 byte;
- formato Linux cooked v2;
- permessi `600`;
- AppArmor mantenuto attivo.

Report pubblico:

- [`../samples/06-cattura-tcpdump-report.md`](../samples/06-cattura-tcpdump-report.md).

Report privato:

```text
reports/06-cattura-tcpdump-private.md
```

## Fase 7 completata — Suricata IDS

Completata e verificata il 20 luglio 2026.

### Installazione e build

```text
Suricata:         8.0.3 RELEASE
suricata-update:  1.3.7
jq:               1.8.1
AF_PACKET:        yes
Hyperscan:        yes
systemd:          yes
```

Suricata è installato sull’host Ubuntu, non in Docker.

### Problemi diagnosticati

La configurazione predefinita usava `eth0`, interfaccia inesistente sul gateway. Sono state inoltre installate le regole inizialmente mancanti.

Configurazione finale anonimizzata:

```yaml
HOME_NET: "[10.42.0.0/24]"

af-packet:
  - interface: wlx<REDACTED>
```

### Regole

Il test finale ha caricato:

```text
2 file di regole
52044 regole corrette
0 regole fallite
52049 firme elaborate
```

### Eventi osservati

Sono stati osservati eventi:

```text
flow, quic, mdns, dns, tls, http, fileinfo, dhcp, stats, alert
```

È stato documentato un alert decoder `SURICATA Ethertype unknown` senza considerarlo automaticamente un attacco.

### Avvio su richiesta

Suricata resta disabilitato al boot.

Durante l’uso:

```text
is-active:  active
is-enabled: disabled
```

Dopo l’arresto:

```text
is-active:  inactive
is-enabled: disabled
```

### Alert locale controllato

Regola:

```text
alert icmp $HOME_NET any -> $HOME_NET any (msg:"LAB Suricata ICMP test"; itype:8; sid:1000001; rev:1;)
```

Un singolo ping broadcast ha prodotto l’alert atteso con:

```text
proto:     ICMP
signature: LAB Suricata ICMP test
action:    allowed
```

### Statistiche

Prova systemd di circa 62 secondi:

```text
packets:          145724
drops:            367
drop percentage:  0.25%
invalid checksum: 0
alerts:           1
```

### Rotazione log

Verificati:

```text
controllo giornaliero tramite logrotate.timer
soglia 1 MiB
14 rotazioni
compressione gzip
copytruncate
```

Il blocco `postrotate` invia HUP soltanto se Suricata è attivo.

La rotazione reale ha creato:

```text
eve.json       nuovo file corrente
eve.json.1.gz  archivio compresso
```

### Documentazione

Guida:

- [`steps/07-suricata.md`](steps/07-suricata.md).

Report pubblico:

- [`../samples/07-suricata-report.md`](../samples/07-suricata-report.md).

Report privato locale:

```text
reports/07-suricata-private.md
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
| 8. Zeek | PROSSIMA |
| 9. Python | DA FARE |
| 10. Docker | DA FARE |
| 11. Test e hardening | DA FARE |

## Prossimi passi immediati

1. copiare il report privato in `reports/07-suricata-private.md`;
2. applicare permessi `600`;
3. verificare `git check-ignore`;
4. eseguire `git fetch` e `git pull --ff-only` per scaricare gli aggiornamenti pubblici;
5. passare a [`steps/08-zeek.md`](steps/08-zeek.md).

## Report pubblici e privati

Nel repository pubblico:

- guide revisionate;
- configurazioni parametrizzate;
- script commentati;
- report principali anonimizzati;
- output brevi e immagini revisionate.

Nella cartella locale `reports/`:

- output integrali;
- nomi reali delle interfacce;
- IP e porte reali;
- query DNS osservate;
- log operativi;
- report personali.

Non pubblicare password, token, MAC, PCAP grezzi, log integrali o traffico di terzi.
