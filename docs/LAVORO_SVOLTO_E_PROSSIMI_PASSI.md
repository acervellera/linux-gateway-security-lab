# Lavoro svolto e prossimi passi

## Funzione del documento

Questo file riassume l'evoluzione reale del gateway fisico Ubuntu e delle fasi operative verificate.

Per lo stato più aggiornato usare [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md). Per comandi, spiegazioni e rollback usare i documenti in [`steps`](steps).

## Gateway fisico

```text
Telefono / dispositivo autorizzato
  -> SecurityGatewayLab
  -> Realtek USB AP
  -> Ubuntu gateway
  -> filtro INPUT e FORWARD nftables
  -> MediaTek wlp13s0
  -> router
  -> Internet
```

## Fase 1 completata — Inventario

Verificati:

- Ubuntu e kernel;
- MediaTek e driver;
- Realtek e driver;
- supporto AP;
- route predefinita;
- rfkill;
- reti Docker.

## Fase 2 completata — Topologia

Piano:

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
```

## Fase 3 completata — Hotspot

Risultati:

- Realtek in modalità AP;
- SSID visibile;
- client reali autenticati e associati;
- indirizzi `10.42.0.x`;
- gateway raggiunto;
- Internet tramite MediaTek;
- profilo fermato, eliminato e ricreato;
- segreto WPA non pubblicato.

## Fase 4 completata — DHCP, routing e NAT

Completata il 16 luglio 2026.

### DHCP e DNS

NetworkManager usa `ipv4.method=shared`. Sono stati osservati:

```text
dnsmasq su 10.42.0.1:53 TCP/UDP
dnsmasq su UDP 67
DHCPDISCOVER
DHCPOFFER
DHCPREQUEST
DHCPACK
```

### Forwarding e NAT

```text
net.ipv4.ip_forward = 1
```

È stata osservata una regola equivalente a:

```text
ip saddr 10.42.0.0/24
ip daddr != 10.42.0.0/24
masquerade
```

### Prima e dopo il NAT

Sulla Realtek:

```text
10.42.0.x:porta -> server:443
```

Sulla MediaTek:

```text
192.168.10.x:porta -> server:443
```

Le catture dimostrano i due lati della traduzione, ma non vengono presentate come lo stesso pacchetto abbinato riga per riga.

### Sicurezza Wi-Fi

Configurazione finale:

```text
key-mgmt: wpa-psk
proto:    rsn
pairwise: ccmp
group:    ccmp
```

## Fase 5 completata — Firewall nftables

Completata il 17 luglio 2026.

### Inventario prima del blocco

Sono state controllate le porte con `ss -lntup`. I servizi rilevanti erano:

```text
DHCP hotspot       UDP 67
DNS hotspot        TCP/UDP 53 su 10.42.0.1
CUPS               TCP 631 solo loopback
mDNS/Avahi         UDP 5353
WS-Discovery/wsdd  UDP 3702
```

`wsdd` è stato identificato come processo di discovery integrato con GVFS. Non è stato rimosso globalmente: il filtro limita soltanto l'accesso proveniente dall'hotspot.

### Filtro INPUT

Il client può:

- ottenere DHCP;
- usare il DNS del gateway;
- usare ICMP verso il gateway;
- ricevere risposte `established,related`.

Il client non può:

- raggiungere altre porte del gateway;
- usare mDNS o WS-Discovery verso Ubuntu tramite l'hotspot.

Test attivo:

```text
client -> 10.42.0.1:631/TCP
risultato: SGW_INPUT_DROP + DROP
```

DHCP, DNS e navigazione sono rimasti funzionanti.

### Filtro FORWARD

Politica verificata:

```text
hotspot -> uplink, new/established/related  ACCEPT
uplink -> hotspot, established/related      ACCEPT
uplink -> hotspot, new                      LOG + DROP
hotspot -> altre interfacce                 LOG + DROP
altre interfacce -> hotspot                 LOG + DROP
invalid sul percorso controllato            DROP
```

Test attivo:

```text
client 10.42.0.x -> 192.168.122.254:80
uscita scelta dal kernel: virbr0
risultato: SGW_FWD_FROM_AP_DROP + DROP
```

Questo dimostra che il client dell'hotspot non può raggiungere la rete privata libvirt, mentre Internet continua a funzionare sull'uplink autorizzato.

### Logging

Prefissi:

```text
SGW_INPUT_DROP
SGW_FWD_FROM_AP_DROP
SGW_FWD_TO_AP_DROP
```

Limite:

```text
5 log/minuto, burst iniziale di 10 pacchetti
```

Il rate limit limita i messaggi, non il numero di pacchetti bloccati.

### Rollback e coesistenza

Le tabelle del progetto sono state eliminate e ricaricate singolarmente. Sono rimaste presenti:

- chain `nm-sh-*` di NetworkManager;
- chain `DOCKER-*`;
- reti e chain libvirt;
- DHCP, DNS e NAT del profilo condiviso.

Non è mai stato usato `nft flush ruleset`.

### Persistenza

Sono stati installati:

```text
/etc/security-gateway-firewall/security-gateway-input-filter.nft
/etc/security-gateway-firewall/security-gateway-filter.nft
/usr/local/sbin/security-gateway-firewall
/etc/systemd/system/security-gateway-firewall.service
```

Lo script supporta `load`, `reload` e `unload`, controlla il batch con `nft --check` e modifica soltanto le due tabelle del progetto.

Il servizio systemd è:

```text
enabled
active (exited)
```

Dopo un riavvio reale sono state ritrovate entrambe le tabelle. Il client ha nuovamente ricevuto DHCP, usato DNS e navigato. Il servizio standard `nftables.service` è rimasto `disabled/inactive`.

### Limiti dichiarati

Non sono stati generati attivamente:

- una nuova connessione da un secondo host dell'uplink verso un client dell'hotspot;
- un pacchetto `ct state invalid` costruito appositamente.

Le relative regole sono presenti. Pochi pacchetti `invalid` reali sono stati osservati e bloccati.

## Stato corrente

| Fase | Stato |
|---:|---|
| 1. Inventario | COMPLETATA |
| 2. Topologia | COMPLETATA |
| 3. Hotspot | COMPLETATA |
| 4. DHCP, routing e NAT | COMPLETATA |
| 5. Firewall nftables | COMPLETATA |
| 6. tcpdump | PROSSIMA |
| 7. Suricata | DA FARE |
| 8. Zeek | DA FARE |
| 9. Python | DA FARE |
| 10. Docker | DA FARE |
| 11. Test e hardening | DA FARE |

## Prossimi passi immediati

La prossima attività è [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md).

Ordine previsto:

1. ripassare il percorso dei pacchetti;
2. studiare la sintassi dei filtri BPF;
3. catturare separatamente hotspot, uplink e bridge virtuali;
4. limitare durata e quantità delle catture;
5. salvare PCAP con permessi appropriati;
6. riconoscere DNS, TCP, TLS e QUIC;
7. confrontare metadati prima e dopo NAT;
8. anonimizzare gli esempi pubblici;
9. preparare materiale per Suricata, Zeek e Python.

## Report pubblici e privati

Nel repository pubblico:

- documentazione revisionata;
- configurazioni parametrizzate;
- script commentato;
- unità systemd revisionata;
- report finale anonimizzato;
- output brevi e immagini ricostruite.

Nella cartella locale `reports/`, ignorata da Git:

- output integrali;
- screenshot originali;
- MAC;
- nome completo della Realtek;
- log del kernel;
- report personali.

Non pubblicare password, token, PCAP grezzi o traffico di terzi.