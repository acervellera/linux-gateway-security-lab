# Fase 6 — Report pubblico cattura tcpdump

**Data di completamento:** 18 luglio 2026  
**Stato:** **COMPLETATA E VERIFICATA**

Questo è l’unico report pubblico principale della fase 6. Riunisce gli esempi realmente osservati durante le catture manuali, con indirizzi locali, nomi completi delle interfacce, porte temporanee e destinazioni remote anonimizzati.

## 1. Obiettivo

Osservare in modo controllato il traffico di un client autorizzato collegato all’hotspot e imparare a riconoscere:

- IP e porte sorgente e destinazione;
- direzione dei pacchetti;
- protocolli DNS, ICMP, TCP e UDP;
- handshake TCP e principali flag;
- traffico cifrato su TCP/443 e UDP/443;
- traduzione NAT sui due lati del gateway;
- salvataggio PCAP limitato;
- vincoli di privacy e interazione con AppArmor.

## 2. Ambiente anonimizzato

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

## 3. Prima cattura limitata

Comando:

```bash
sudo tcpdump -ni "$AP_IF" -c 5 "host $CLIENT_IP"
```

Significato:

- `sudo`: consente l’accesso alla cattura di rete;
- `-n`: evita la risoluzione degli IP in nomi;
- `-i`: seleziona l’interfaccia;
- `-c 5`: termina dopo cinque pacchetti;
- `host $CLIENT_IP`: limita il filtro al client autorizzato.

Estratto anonimizzato:

```text
10.42.0.x.PORTA > REMOTE_IP_A.443: UDP, length 68
REMOTE_IP_A.443 > 10.42.0.x.PORTA: UDP, length 80
10.42.0.x.PORTA > REMOTE_IP_A.443: UDP, length 55
REMOTE_IP_A.443 > 10.42.0.x.PORTA: UDP, length 80
10.42.0.x.PORTA > REMOTE_IP_B.443: Flags [R.], length 0
```

Interpretazione:

```text
IP_sorgente.porta_sorgente > IP_destinazione.porta_destinazione
```

Il traffico UDP verso la porta 443 è compatibile con QUIC/HTTP/3, ma la porta da sola non costituisce una prova assoluta. Il contenuto applicativo resta cifrato. `Flags [R.]` indica RST + ACK e rappresenta un reset o una chiusura immediata, non l’handshake iniziale.

Statistiche:

```text
5 packets captured
5 packets received by filter
0 packets dropped by kernel
```

## 4. Consultazione WHOIS

Comando usato su un indirizzo remoto osservato:

```bash
whois <REMOTE_IP>
```

Campi utili:

```text
NetRange       intervallo registrato
CIDR           blocco di rete
NetName        nome amministrativo del blocco
Organization   organizzazione registrataria
Country        dato amministrativo della registrazione
```

Una consultazione ha associato il blocco a `Facebook, Inc.`. La conclusione corretta è che l’indirizzo apparteneva a una rete registrata a tale organizzazione. Il solo WHOIS non dimostra quale applicazione fosse in uso, quale persona generasse il traffico, la posizione fisica certa del server o il contenuto della comunicazione.

## 5. DNS tradizionale

Comando:

```bash
sudo tcpdump \
    -i "$AP_IF" \
    -n \
    -vv \
    -c 12 \
    "host $CLIENT_IP and (udp port 53 or tcp port 53)"
```

Estratto anonimizzato:

```text
10.42.0.x.PORTA > 10.42.0.1.53: ID+ HTTPS? servizio.example.
10.42.0.x.PORTA > 10.42.0.1.53: ID+ A? servizio.example.
10.42.0.1.53 > 10.42.0.x.PORTA: ID ... CNAME ... A IPV4_REMOTO
10.42.0.1.53 > 10.42.0.x.PORTA: ID ... CNAME ... A ... AAAA ...
```

Sono stati riconosciuti:

- `A`: indirizzo IPv4;
- `AAAA`: indirizzo IPv6;
- `CNAME`: alias verso un altro nome;
- `HTTPS`: record DNS con informazioni sul servizio HTTPS, distinto dal contenuto HTTPS;
- identificativo di transazione uguale nella domanda e nella risposta;
- porta temporanea del client e porta DNS 53 del gateway.

La cattura ha mostrato che il DNS tradizionale può rivelare i nomi interrogati anche quando il successivo traffico applicativo è cifrato. Una query può comunque essere generata automaticamente dal sistema operativo o da un’applicazione in background.

Risultato:

```text
8 packets captured
8 packets received by filter
0 packets dropped by kernel
```

## 6. ICMP

Cattura:

```bash
sudo tcpdump \
    -i "$AP_IF" \
    -n \
    -vv \
    -c 6 \
    "icmp and host $CLIENT_IP"
```

Traffico generato:

```bash
ping -I "$AP_IF" -c 3 "$CLIENT_IP"
```

Estratto anonimizzato:

```text
10.42.0.1 > 10.42.0.x: ICMP echo request, id ID_ICMP, seq 1, length 64
10.42.0.1 > 10.42.0.x: ICMP echo request, id ID_ICMP, seq 2, length 64
10.42.0.1 > 10.42.0.x: ICMP echo request, id ID_ICMP, seq 3, length 64
```

Risultato:

```text
3 packets transmitted, 0 received, 100% packet loss
```

La cattura dimostra che il gateway ha trasmesso le tre richieste sull’interfaccia hotspot. Il telefono non ha inviato `echo reply`. Questa assenza non dimostra da sola un problema di routing o firewall, perché molti dispositivi mobili ignorano ICMP in ingresso.

## 7. Handshake TCP

Comando:

```bash
sudo tcpdump \
    -i "$AP_IF" \
    -n \
    -vv \
    -c 30 \
    "host $CLIENT_IP and tcp and (port 80 or port 443)"
```

Handshake completo anonimizzato:

```text
10.42.0.x.PORTA > REMOTE_IP.443: Flags [SEW], seq N, length 0
REMOTE_IP.443 > 10.42.0.x.PORTA: Flags [S.], seq M, ack N+1, length 0
10.42.0.x.PORTA > REMOTE_IP.443: Flags [.], seq 1, ack 1, length 0
```

Sequenza:

```text
client -> server  SYN
server -> client  SYN + ACK
client -> server  ACK
```

Flag riconosciuti:

- `S`: SYN;
- `.`: ACK;
- `E`: ECE, collegato a ECN;
- `W`: CWR, collegato a ECN;
- `P.`: PSH + ACK;
- `F.`: FIN + ACK;
- `R`: RST.

Dopo l’handshake sono stati osservati segmenti dati e ACK cumulativi. La porta TCP 443 e la sequenza dei pacchetti sono compatibili con TLS, ma il contenuto applicativo non è stato decifrato.

Statistiche:

```text
30 packets captured
34 packets received by filter
0 packets dropped by kernel
```

## 8. Confronto prima e dopo il NAT

Comando:

```bash
sudo tcpdump \
    -i any \
    -nn \
    -tttt \
    -vv \
    -c 80 \
    "((host $CLIENT_IP) or (host $UPLINK_IP)) and
     (tcp port 80 or tcp port 443 or udp port 443)"
```

Il messaggio sulla modalità promiscua non supportata da `any` è informativo. `any` è un dispositivo virtuale che usa Linux cooked capture.

Stesso datagramma in uscita:

```text
wlx<REDACTED> In  10.42.0.x.PORTA    > REMOTE_IP.443: UDP, length L
wlp13s0 Out       192.168.10.x.PORTA > REMOTE_IP.443: UDP, length L
```

Risposta:

```text
wlp13s0 In        REMOTE_IP.443 > 192.168.10.x.PORTA: UDP, length R
wlx<REDACTED> Out REMOTE_IP.443 > 10.42.0.x.PORTA: UDP, length R
```

Il NAT ha sostituito l’IP sorgente privato del client con l’IP dell’uplink. Al ritorno, conntrack ha ripristinato la destinazione originale. La porta è rimasta invariata negli esempi osservati, ma il NAT può tradurla quando necessario.

È stato osservato anche il decremento del TTL:

```text
hotspot In  ttl 64 -> uplink Out ttl 63
uplink In   ttl 82 -> hotspot Out ttl 81
```

Statistiche:

```text
80 packets captured
111 packets received by filter
0 packets dropped by kernel
```

## 9. PCAP controllato e AppArmor

Il PCAP privato è stato prodotto fuori dal repository con:

- massimo 20 record;
- filtro UDP porta 443;
- snapshot length di 128 byte;
- formato PCAP 2.4, Linux cooked v2;
- dimensione di circa 2,8 KiB;
- permessi finali `600`.

Poiché il profilo AppArmor `tcpdump` impediva la creazione e l’apertura diretta nella cartella privata, è stata usata una pipe senza disabilitare AppArmor:

```bash
set -o pipefail

sudo tcpdump \
    -i any \
    -nn \
    -s 128 \
    -c 20 \
    -w - \
    "((host $CLIENT_IP) or (host $UPLINK_IP)) and udp port 443" \
    | dd of="$PCAP_FILE" status=none
```

Lettura:

```bash
tcpdump -nn -tttt -r - < "$PCAP_FILE"
```

Il journal ha confermato negazioni AppArmor per `mknod`, `open` e `dac_read_search`. Il profilo è rimasto attivo. `-s 128` limita i byte materialmente salvati, anche quando tcpdump mostra la lunghezza originale del datagramma.

## 10. Risultati finali

- [x] traffico del client catturato con limiti precisi;
- [x] IP, porte e direzioni interpretati;
- [x] DNS tradizionale osservato;
- [x] record `A`, `AAAA`, `CNAME` e `HTTPS` riconosciuti;
- [x] richieste ICMP osservate;
- [x] assenza di risposta ICMP documentata senza attribuirla automaticamente a un guasto;
- [x] handshake TCP completo riconosciuto;
- [x] traffico TCP/443 e UDP/443 riconosciuto come cifrato;
- [x] NAT verificato riga per riga sui due lati;
- [x] traduzione inversa e decremento TTL verificati;
- [x] PCAP limitato creato e letto;
- [x] AppArmor mantenuto attivo;
- [x] nessun PCAP grezzo pubblicato;
- [x] nessun pacchetto perso dal kernel nelle catture documentate.

## 11. Privacy

Non pubblicare:

- indirizzi MAC;
- nome completo dell’interfaccia Realtek;
- IP locali completi non necessari;
- porte temporanee associate a sessioni reali;
- destinazioni remote integrali;
- query DNS personali;
- log integrali;
- PCAP grezzi;
- hostname e percorsi personali.

I materiali completi devono restare nella cartella locale `reports/`, ignorata da Git, oppure in una directory privata esterna al repository.