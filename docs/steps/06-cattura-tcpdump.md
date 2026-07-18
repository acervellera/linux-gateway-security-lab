# Fase 6 — Cattura del traffico con tcpdump

## Stato

```text
COMPLETATA E VERIFICATA — 18 luglio 2026
```

## Obiettivo raggiunto

È stato osservato in modo controllato il traffico del client autorizzato collegato all’hotspot, riconoscendo protocolli, direzioni, handshake TCP, richieste DNS, traffico cifrato e traduzione NAT sui due lati del gateway.

## Concetti verificati

- pacchetti IPv4 e direzione sorgente/destinazione;
- interfacce di ingresso e uscita;
- filtri BPF;
- DNS tradizionale su porta 53;
- TCP, UDP e ICMP;
- traffico cifrato TCP/443 e UDP/443;
- record DNS `A`, `AAAA`, `CNAME` e `HTTPS`;
- handshake TCP SYN, SYN-ACK e ACK;
- flag TCP ACK, PSH, FIN e RST;
- indirizzi prima e dopo il NAT;
- decremento del TTL durante il forwarding;
- snapshot length e formato PCAP;
- limiti di privacy;
- interazione tra `tcpdump` e AppArmor.

## Ambiente anonimizzato

```text
AP_IF=wlx<REDACTED>
UPLINK_IF=wlp13s0
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
CLIENT_IP=10.42.0.x
UPLINK_IP=192.168.10.x
```

## Comandi principali verificati

### Traffico del client

```bash
sudo tcpdump -ni "$AP_IF" -c 5 "host $CLIENT_IP"
```

### DNS tradizionale

```bash
sudo tcpdump \
    -i "$AP_IF" \
    -n \
    -vv \
    -c 12 \
    "host $CLIENT_IP and (udp port 53 or tcp port 53)"
```

Sono state osservate domande e risposte con record `A`, `AAAA`, `CNAME` e `HTTPS`.

### ICMP

```bash
sudo tcpdump \
    -i "$AP_IF" \
    -n \
    -vv \
    -c 6 \
    "icmp and host $CLIENT_IP"
```

Sono state osservate tre richieste Echo dal gateway verso il client. Il telefono non ha risposto; la cattura ha comunque dimostrato che i pacchetti sono stati trasmessi sull’interfaccia hotspot.

### Handshake TCP

```bash
sudo tcpdump \
    -i "$AP_IF" \
    -n \
    -vv \
    -c 30 \
    "host $CLIENT_IP and tcp and (port 80 or port 443)"
```

Sequenza riconosciuta:

```text
client -> server  SYN
server -> client  SYN-ACK
client -> server  ACK
```

Sono stati osservati anche dati cifrati successivi e flag TCP `PSH`, `FIN` e `RST`.

## Confronto prima e dopo il NAT

Cattura simultanea:

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

Flusso in uscita:

```text
wlx<REDACTED> In  10.42.0.x:PORTA    -> IP_REMOTO:443
wlp13s0 Out       192.168.10.x:PORTA -> IP_REMOTO:443
```

Percorso inverso:

```text
wlp13s0 In        IP_REMOTO:443 -> 192.168.10.x:PORTA
wlx<REDACTED> Out IP_REMOTO:443 -> 10.42.0.x:PORTA
```

Il TTL è diminuito di uno durante il forwarding, confermando il passaggio attraverso Ubuntu come router.

## PCAP controllato

Il file privato è stato salvato fuori dal repository con:

- filtro preciso;
- massimo 20 record;
- snapshot length di 128 byte;
- formato PCAP 2.4, Linux cooked v2;
- permessi finali `600`;
- dimensione di circa 2,8 KiB;
- nessuna pubblicazione del file grezzo.

A causa del profilo AppArmor attivo, `tcpdump` non poteva creare o aprire direttamente il file nella cartella privata. La cattura e la lettura sono state completate senza modificare AppArmor:

```bash
sudo tcpdump ... -w - | dd of="$PCAP_FILE" status=none

tcpdump -nn -tttt -r - < "$PCAP_FILE"
```

## Report pubblico

Unico report principale:

- [`../../samples/06-cattura-tcpdump-report.md`](../../samples/06-cattura-tcpdump-report.md).

Il report riunisce gli esempi DNS, ICMP, handshake TCP, NAT, PCAP e AppArmor. I precedenti frammenti separati sono stati incorporati e rimossi.

## Report privato

Il report completo con valori locali deve essere conservato esclusivamente in:

```text
reports/06-cattura-tcpdump-private.md
```

La cartella `reports/` è ignorata da Git. Il PCAP resta nella directory privata esterna al repository.

## Test di completamento

- [x] richiesta e risposta DNS osservate;
- [x] richieste ICMP osservate;
- [x] assenza di risposta ICMP documentata correttamente;
- [x] handshake TCP completo osservato;
- [x] traffico cifrato riconosciuto senza decifrarlo;
- [x] stesso flusso riconosciuto sui due lati;
- [x] effetto del NAT compreso;
- [x] PCAP limitato creato e revisionato;
- [x] AppArmor mantenuto attivo;
- [x] nessun PCAP sensibile pubblicato;
- [x] nessun pacchetto perso dal kernel nelle catture documentate.

## Privacy

Non pubblicare:

- indirizzi MAC reali;
- nome completo dell’interfaccia Realtek;
- IP e porte completi non necessari;
- PCAP grezzi;
- log integrali;
- query DNS personali;
- hostname e percorsi locali.

## Rollback

`tcpdump` non modifica la rete. Terminare la cattura con `Ctrl+C` e rimuovere in modo sicuro eventuali file non più necessari.

## Prossimo passo

Fase 7: installare e configurare Suricata inizialmente in modalità passiva IDS, dopo aver verificato che tutta la documentazione della fase 6 sia aggiornata e che il report privato resti fuori da Git.