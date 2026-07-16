# Lavoro svolto e prossimi passi

## Funzione del documento

Questo file riassume l'evoluzione reale del progetto:

- gateway fisico Ubuntu;
- fasi operative verificate.

Per lo stato più aggiornato usare [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md). Per comandi e rollback usare [`steps`](steps).

## Gateway fisico

```text
Telefono / dispositivo autorizzato
  -> SecurityGatewayLab
  -> Realtek USB AP
  -> Ubuntu gateway
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

NetworkManager usa:

```text
ipv4.method=shared
```

Sono stati osservati:

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

Le catture sono state eseguite in momenti diversi. Dimostrano i due lati della traduzione, ma non vengono presentate come lo stesso pacchetto abbinato riga per riga.

### DNS e cifratura

È stata osservata una richiesta DNS tradizionale per `time.apple.com`, leggibile sulla porta 53.

Sono stati osservati TCP 443 e UDP 443. Le catture mostravano metadati, non password o contenuto applicativo.

### Sicurezza Wi-Fi

Configurazione iniziale:

```text
key-mgmt: wpa-psk
proto:    --
pairwise: --
group:    --
```

iOS segnalava una configurazione compatibile con TKIP.

Configurazione finale:

```text
key-mgmt: wpa-psk
proto:    rsn
pairwise: ccmp
group:    ccmp
```

Dopo la riconnessione l'avviso è scomparso.

### Percorso verificato

Con dati cellulari disabilitati:

```text
client
  -> Realtek
  -> Ubuntu
  -> MediaTek
  -> Internet
```

## Stato corrente

| Fase | Stato |
|---:|---|
| 1. Inventario | COMPLETATA |
| 2. Topologia | COMPLETATA |
| 3. Hotspot | COMPLETATA |
| 4. DHCP, routing e NAT | COMPLETATA |
| 5. Firewall nftables | PROSSIMA |
| 6. tcpdump | DA FARE |
| 7. Suricata | DA FARE |
| 8. Zeek | DA FARE |
| 9. Python | DA FARE |
| 10. Docker | DA FARE |
| 11. Test e hardening | DA FARE |

## Prossimi passi immediati

La prossima attività è [`steps/05-firewall-nftables.md`](steps/05-firewall-nftables.md).

Ordine previsto:

1. salvare il ruleset corrente;
2. riconoscere le regole gestite da NetworkManager e Docker;
3. preparare rollback;
4. applicare policy stateful;
5. consentire `established,related`;
6. limitare hotspot → uplink;
7. proteggere gateway e rete domestica;
8. verificare DHCP, DNS e Internet;
9. documentare output reali.

## Report pubblici e privati

Nel repository pubblico:

- documentazione revisionata;
- sample anonimizzati;
- output brevi;
- immagini ricostruite.

Nella cartella locale `reports/`, ignorata da Git:

- output integrali;
- screenshot originali;
- MAC;
- nome completo della Realtek;
- note personali.

Non pubblicare password, token, PCAP grezzi o traffico di terzi.
