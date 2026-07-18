# Fase 6 — Report pubblico cattura tcpdump

**Data di avvio:** 18 luglio 2026  
**Stato:** **IN CORSO**

Questo report documenta prove reali eseguite sul gateway Ubuntu fisico. I nomi completi delle interfacce, gli indirizzi MAC, gli identificativi del dispositivo e gli eventuali dati sensibili vengono rimossi o anonimizzati.

## 1. Obiettivo della fase

Osservare in modo controllato il traffico del client autorizzato collegato all'hotspot e imparare a riconoscere:

- indirizzi IP sorgente e destinazione;
- porte sorgente e destinazione;
- direzione dei pacchetti;
- protocolli TCP e UDP;
- traffico web cifrato su porta 443;
- differenza tra traffico prima e dopo il NAT;
- informazioni ottenibili tramite WHOIS senza attribuire un IP a una persona specifica.

## 2. Ambiente verificato

Valori pubblicabili:

```text
AP_IF=wlx<REDACTED>
UPLINK_IF=wlp13s0
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
CLIENT_IP=10.42.0.x
UPLINK_IP=192.168.10.x
```

Versioni osservate:

```text
tcpdump 4.99.6
libpcap 1.10.6
OpenSSL 3.5.5
```

## 3. Prima cattura limitata del client

Comando eseguito:

```bash
sudo tcpdump -ni "$AP_IF" -c 5 "host $CLIENT_IP"
```

Opzioni:

- `-n`: non risolve indirizzi e porte in nomi;
- `-i`: seleziona l'interfaccia di cattura;
- `-c 5`: termina automaticamente dopo cinque pacchetti;
- `host $CLIENT_IP`: limita la cattura al solo client autorizzato.

Estratto anonimizzato:

```text
IP 10.42.0.x.56988 > 163.70.128.63.443: UDP, length 68
IP 163.70.128.63.443 > 10.42.0.x.56988: UDP, length 80
IP 10.42.0.x.56988 > 163.70.128.63.443: UDP, length 55
IP 163.70.128.63.443 > 10.42.0.x.56988: UDP, length 80
IP 10.42.0.x.57856 > 157.240.231.175.443: Flags [R.], length 0
```

Statistiche:

```text
5 packets captured
5 packets received by filter
0 packets dropped by kernel
```

## 4. Interpretazione di IP e porte

La forma mostrata da tcpdump è:

```text
IP_sorgente.porta_sorgente > IP_destinazione.porta_destinazione
```

Esempio:

```text
10.42.0.x.56988 > 163.70.128.63.443
```

Interpretazione:

```text
10.42.0.x     indirizzo privato del client nell'hotspot
56988         porta temporanea scelta dal client
>             direzione del pacchetto
163.70.128.63 indirizzo pubblico remoto
443           porta normalmente associata a traffico web cifrato
```

La riga inversa rappresenta una risposta dal server remoto verso il client.

Il traffico UDP verso la porta 443 è compatibile con QUIC/HTTP3, ma la sola porta non costituisce una prova assoluta del protocollo applicativo. Il contenuto resta cifrato.

Il pacchetto TCP con `Flags [R.]` contiene i flag RST e ACK e rappresenta la chiusura o il reset di una connessione, non il normale handshake iniziale.

## 5. Esempio reale di consultazione WHOIS

Comando:

```bash
whois 157.240.231.175
```

Campi significativi osservati:

```text
NetRange:     157.240.0.0 - 157.240.255.255
CIDR:         157.240.0.0/16
NetName:      THEFA-3
Organization: Facebook, Inc.
Country:      US
```

Interpretazione:

- `NetRange` indica l'intervallo di indirizzi registrato;
- `CIDR /16` rappresenta il blocco di rete `157.240.0.0/16`;
- `NetName` è il nome amministrativo del blocco;
- `Organization` indica l'organizzazione registrataria della rete;
- `Country` descrive il dato amministrativo della registrazione, non la posizione fisica certa del singolo server.

Conclusione corretta:

```text
L'indirizzo appartiene a un blocco registrato a Facebook, Inc.
```

Conclusioni non giustificate dal solo WHOIS:

```text
una persona specifica stava usando una determinata applicazione;
il server era fisicamente nell'indirizzo postale mostrato;
la posizione geografica del singolo IP è certa;
il contenuto della comunicazione è noto.
```

## 6. Risultati parziali

- [x] tcpdump installato e funzionante;
- [x] interfaccia hotspot identificata;
- [x] uplink identificato;
- [x] client autorizzato identificato;
- [x] cattura limitata a cinque pacchetti;
- [x] traffico in uscita e risposte osservati;
- [x] UDP 443 compatibile con QUIC riconosciuto;
- [x] TCP RST/ACK riconosciuto;
- [x] proprietario amministrativo di un blocco IP verificato tramite WHOIS;
- [ ] richiesta DNS tradizionale osservata;
- [ ] ping ICMP osservato;
- [ ] handshake TCP completo osservato;
- [ ] stesso flusso confrontato prima e dopo il NAT;
- [ ] PCAP controllato salvato e revisionato.

## 7. Privacy

Non pubblicare:

- indirizzi MAC reali;
- nome completo dell'interfaccia Realtek;
- PCAP grezzi;
- log integrali non revisionati;
- hostname, query DNS o dati applicativi sensibili;
- informazioni che possano identificare il dispositivo o il proprietario.
