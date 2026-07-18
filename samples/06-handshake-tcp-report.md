# Fase 6 — Estratto handshake TCP

**Data:** 18 luglio 2026  
**Stato:** verifica completata

Questo estratto integra il report pubblico della fase 6 con una cattura reale e anonimizzata del three-way handshake TCP. Il nome completo dell'interfaccia hotspot e l'indirizzo completo del client sono rimossi.

## Comando

```bash
sudo tcpdump \
    -i "$AP_IF" \
    -n \
    -vv \
    -c 30 \
    "host $CLIENT_IP and tcp and (port 80 or port 443)"
```

## Handshake completo osservato

È stata scelta una singola connessione identificata dalla stessa coppia di indirizzi e porte:

```text
10.42.0.x:54458 <-> 142.251.27.139:443
```

Estratto:

```text
10.42.0.x.54458 > 142.251.27.139.443: Flags [SEW], seq 164758071, length 0
142.251.27.139.443 > 10.42.0.x.54458: Flags [S.], seq 2405883276, ack 164758072, length 0
10.42.0.x.54458 > 142.251.27.139.443: Flags [.], seq 1, ack 1, length 0
```

Interpretazione:

```text
client -> server   SYN
server -> client   SYN + ACK
client -> server   ACK
```

La connessione TCP risulta quindi stabilita correttamente.

## Significato dei flag

- `S` indica SYN, usato per iniziare e sincronizzare una connessione TCP;
- `.` indica ACK;
- `E` indica ECE, legato alla segnalazione ECN;
- `W` indica CWR, anch'esso legato a ECN;
- `P.` indica PSH + ACK, normalmente un segmento che trasporta dati da consegnare all'applicazione;
- `F.` indica FIN + ACK, richiesta di chiusura ordinata;
- `R` indica RST, chiusura o annullamento immediato della connessione.

Il primo pacchetto appare come `Flags [SEW]` e non soltanto `[S]` perché il client propone anche l'uso di ECN durante l'apertura della connessione. Il server risponde con `Flags [S.E]`, confermando SYN, ACK ed ECE.

## Numeri di sequenza e ACK

Nel primo SYN il client usa:

```text
seq 164758071
```

Il server risponde con:

```text
ack 164758072
```

L'ACK vale sequenza iniziale + 1 perché il flag SYN consuma una posizione nello spazio dei numeri di sequenza TCP.

Tcpdump mostra poi numeri relativi:

```text
seq 1
ack 1
```

per rendere più semplice seguire la connessione dopo l'handshake.

## Dati successivi all'handshake

Subito dopo il terzo pacchetto sono stati osservati segmenti con contenuto:

```text
10.42.0.x.54458 > 142.251.27.139.443: Flags [.], seq 1:1401, ack 1, length 1400
10.42.0.x.54458 > 142.251.27.139.443: Flags [P.], seq 1401:1543, ack 1, length 142
```

`seq 1:1401` significa che il segmento trasporta i byte con numerazione relativa da 1 fino a 1400. La differenza tra i due estremi è infatti 1400 byte.

Poiché la destinazione usa TCP 443, questi dati sono compatibili con l'avvio di una sessione TLS. La cattura permette di osservare metadati, dimensioni, direzioni e timing, ma non il contenuto applicativo in chiaro.

## Risposte del server

Il server ha successivamente inviato più segmenti di dati, per esempio:

```text
142.251.27.139.443 > 10.42.0.x.54458: Flags [.], seq 1:1401, ack 1543, length 1400
142.251.27.139.443 > 10.42.0.x.54458: Flags [P.], seq 1401:2801, ack 1543, length 1400
```

L'ACK `1543` conferma che il server ha ricevuto i byte inviati dal client fino al numero relativo 1542 e si aspetta il byte 1543.

Il client ha poi confermato i dati ricevuti con ACK cumulativi, tra cui:

```text
ack 2801
ack 6260
```

Un ACK cumulativo conferma la ricezione di tutti i byte precedenti al numero indicato.

## Connessioni annullate

Nella stessa cattura sono apparse anche connessioni terminate con `RST`. Per esempio, una porta temporanea ha inviato SYN, ricevuto SYN-ACK e poi risposto con RST. Questo può accadere quando un'applicazione avvia tentativi paralleli e annulla quelli non più necessari.

Non costituisce, da solo, prova di errore o attività ostile.

## Statistiche

```text
30 packets captured
34 packets received by filter
0 packets dropped by kernel
```

`30 packets captured` corrisponde al limite richiesto con `-c 30`. Il filtro ha ricevuto almeno 34 pacchetti prima dell'arresto, mentre il kernel non ha segnalato perdite.

## Risultato

- [x] SYN osservato;
- [x] SYN-ACK osservato;
- [x] ACK finale osservato;
- [x] handshake TCP completo verificato;
- [x] traffico dati successivo riconosciuto;
- [x] ACK cumulativi riconosciuti;
- [x] chiusure FIN e RST riconosciute;
- [x] nessun pacchetto perso dal kernel durante la cattura.
