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

Verificati:

- `dnsmasq` su DHCP e DNS;
- sequenza DHCP completa;
- `net.ipv4.ip_forward=1`;
- masquerading per `10.42.0.0/24`;
- traffico sui lati Realtek e MediaTek;
- DNS classico;
- TCP 443 e UDP 443;
- WPA2-RSN con CCMP/AES.

Percorso:

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

### Catture limitate

Sono stati usati filtri BPF con limiti di pacchetti, evitando catture indefinite. Nelle catture documentate il kernel ha sempre riportato zero pacchetti persi.

### DNS

Osservati:

- richieste e risposte sulla porta 53;
- record `A`, `AAAA`, `CNAME` e `HTTPS`;
- nomi Apple/iCloud generati dal dispositivo;
- differenza tra DNS visibile e contenuto HTTPS cifrato.

### ICMP

Il gateway ha inviato tre richieste Echo al telefono. Il telefono non ha risposto. La cattura ha dimostrato la trasmissione sulla Realtek senza attribuire automaticamente l’assenza di risposta a un guasto della rete.

### TCP

Riconosciuto un handshake completo:

```text
SYN -> SYN-ACK -> ACK
```

Osservati anche ACK cumulativi e flag PSH, FIN e RST. Il traffico sulla porta 443 è rimasto cifrato.

### NAT riga per riga

La cattura `-i any` ha mostrato lo stesso datagramma sui due lati:

```text
wlx<REDACTED> In  10.42.0.x:PORTA    -> IP_REMOTO:443
wlp13s0 Out       192.168.10.x:PORTA -> IP_REMOTO:443
```

Risposta:

```text
wlp13s0 In        IP_REMOTO:443 -> 192.168.10.x:PORTA
wlx<REDACTED> Out IP_REMOTO:443 -> 10.42.0.x:PORTA
```

Il TTL è diminuito di uno durante il forwarding.

### PCAP privato

Creato un file PCAP con:

```text
20 record
snapshot 128 byte
formato PCAP 2.4
Linux cooked v2
permessi 600
dimensione circa 2,8 KiB
```

AppArmor ha bloccato creazione e lettura diretta da parte di `tcpdump`. La protezione non è stata disabilitata: i dati sono stati trasferiti tramite standard output e standard input.

### Documentazione

Unico report pubblico:

- [`../samples/06-cattura-tcpdump-report.md`](../samples/06-cattura-tcpdump-report.md).

Report privato locale:

```text
reports/06-cattura-tcpdump-private.md
```

Il report privato e il PCAP non devono essere aggiunti a Git.

## Stato corrente

| Fase | Stato |
|---:|---|
| 1. Inventario | COMPLETATA |
| 2. Topologia | COMPLETATA |
| 3. Hotspot | COMPLETATA |
| 4. DHCP, routing e NAT | COMPLETATA |
| 5. Firewall nftables | COMPLETATA |
| 6. tcpdump | COMPLETATA |
| 7. Suricata | PROSSIMA |
| 8. Zeek | DA FARE |
| 9. Python | DA FARE |
| 10. Docker | DA FARE |
| 11. Test e hardening | DA FARE |

## Prossimi passi immediati

Prima della fase 7:

1. copiare il report privato in `reports/06-cattura-tcpdump-private.md`;
2. applicare permessi `600`;
3. verificare `git check-ignore`;
4. controllare che non esistano PCAP tracciati;
5. eseguire `git status`.

Poi seguire [`steps/07-suricata.md`](steps/07-suricata.md) iniziando in modalità passiva IDS, senza bloccare il traffico.

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
- log AppArmor;
- report personali.

Non pubblicare password, token, MAC, PCAP grezzi o traffico di terzi.