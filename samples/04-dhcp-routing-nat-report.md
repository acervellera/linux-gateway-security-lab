# Report pubblico anonimizzato — Fase 4

Data verifica: 16 luglio 2026  
Fase: DHCP, routing IPv4 e NAT  
Esito: completata e verificata

## Scopo

Dimostrare con output reali che un client collegato alla Realtek:

- riceve un indirizzo tramite DHCP;
- usa Ubuntu come gateway e DNS;
- viene inoltrato sulla MediaTek;
- raggiunge Internet tramite NAT;
- mantiene il traffico HTTPS/QUIC cifrato;
- usa WPA2-RSN con CCMP/AES.

## Architettura

```text
Client 10.42.0.x
      |
      v
Realtek AP 10.42.0.1
      |
      | forwarding + NAT
      v
MediaTek 192.168.10.x
      |
      v
Internet
```

## Parametri pubblicabili

```text
AP_IF=wlx<REDACTED>
UPLINK_IF=wlp13s0
HOTSPOT_PROFILE=security-gateway-ap
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
UPLINK_GATEWAY=192.168.10.1
```

## DHCP e DNS

NetworkManager usa `ipv4.method=shared` e ha avviato `dnsmasq`.

Porte osservate:

```text
10.42.0.1:53/tcp
10.42.0.1:53/udp
0.0.0.0:67/udp
```

La sequenza DHCP osservata è stata:

```text
DHCPDISCOVER
DHCPOFFER
DHCPREQUEST
DHCPACK
```

## Forwarding

```text
net.ipv4.ip_forward = 1
```

Il valore era già attivo e non è stato modificato manualmente.

## NAT

La regola automatica osservata era equivalente a:

```text
ip saddr 10.42.0.0/24
ip daddr != 10.42.0.0/24
masquerade
```

I contatori non nulli hanno confermato traffico reale.

## Prima del NAT

Cattura sulla Realtek:

```text
10.42.0.x:PORTA_CLIENT > SERVER:443
SERVER:443 > 10.42.0.x:PORTA_CLIENT
```

Il gateway vede l'indirizzo interno del client.

## Dopo il NAT

Cattura sulla MediaTek:

```text
192.168.10.x:PORTA_ESTERNA > SERVER:443
SERVER:443 > 192.168.10.x:PORTA_ESTERNA
```

Il server remoto vede l'indirizzo del gateway sull'uplink.

Le due catture pubblicate sono esempi presi in momenti diversi e non rappresentano lo stesso pacchetto abbinato riga per riga.

## DNS leggibile

Esempio anonimizzato:

```text
10.42.0.x:PORTA > 10.42.0.1:53
A? time.apple.com.

10.42.0.1:53 > 10.42.0.x:PORTA
CNAME time.g.aaplimg.com.
A 17.253.x.x
```

Il DNS tradizionale è leggibile dal gateway.

## HTTPS e QUIC

Sono stati osservati:

```text
TCP 443
UDP 443
```

Gli IP, le porte, i tempi e le dimensioni erano visibili. Password, cookie e contenuto applicativo non erano leggibili nella cattura passiva.

## Sicurezza Wi-Fi prima

L'iPhone segnalava una configurazione compatibile con WPA/WPA2-TKIP:

![Prima della correzione](../docs/images/04-wifi-security-before.svg)

## Correzione

```bash
sudo nmcli connection modify security-gateway-ap \
    802-11-wireless-security.key-mgmt wpa-psk \
    802-11-wireless-security.proto rsn \
    802-11-wireless-security.pairwise ccmp \
    802-11-wireless-security.group ccmp
```

Verifica:

```text
key-mgmt: wpa-psk
proto:    rsn
pairwise: ccmp
group:    ccmp
```

## Sicurezza Wi-Fi dopo

Dopo la riconnessione l'avviso è scomparso:

![Dopo la correzione](../docs/images/04-wifi-security-after.svg)

Le immagini sono ricostruzioni anonimizzate e non contengono MAC, password o barra di stato.

## Esito

- [x] DHCP verificato;
- [x] DNS verificato;
- [x] forwarding verificato;
- [x] NAT verificato;
- [x] cattura prima e dopo il NAT;
- [x] DNS classico osservato;
- [x] HTTPS/QUIC non leggibile in chiaro;
- [x] dati cellulari disabilitati durante il test;
- [x] WPA2-RSN/CCMP applicato;
- [x] avviso iOS eliminato.

## Privacy

Sono stati rimossi:

- MAC reali;
- nome completo della Realtek;
- IP completo dell'host;
- password;
- hostname e percorsi personali;
- output integrali e PCAP grezzi.
