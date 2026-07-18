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
- richieste e risposte DNS tradizionali;
- record DNS `A`, `AAAA`, `CNAME` e `HTTPS`;
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

## 6. Cattura DNS tradizionale

Comando eseguito:

```bash
sudo tcpdump \
    -i "$AP_IF" \
    -n \
    -vv \
    -c 12 \
    "host $CLIENT_IP and (udp port 53 or tcp port 53)"
```

Il filtro combina tre condizioni:

- il pacchetto deve appartenere al client autorizzato;
- deve usare la porta DNS 53;
- può usare UDP oppure TCP.

La cattura è stata interrotta manualmente dopo otto pacchetti:

```text
8 packets captured
8 packets received by filter
0 packets dropped by kernel
```

Estratto anonimizzato:

```text
10.42.0.x.60253 > 10.42.0.1.53: 6469+ HTTPS? mesu.apple.com.
10.42.0.x.55405 > 10.42.0.1.53: 35583+ A? mesu.apple.com.
10.42.0.1.53 > 10.42.0.x.55405: 35583 ... CNAME ... A 23.60.188.50
10.42.0.x.52925 > 10.42.0.1.53: 60270+ HTTPS? mask-api.icloud.com.
10.42.0.x.60128 > 10.42.0.1.53: 28287+ A? mask-api.icloud.com.
10.42.0.1.53 > 10.42.0.x.52925: 60270 ... CNAME ... A ... AAAA ...
10.42.0.1.53 > 10.42.0.x.60128: 28287 ... CNAME ... A ...
```

### 6.1 Direzione e ruoli

Esempio di richiesta:

```text
10.42.0.x.55405 > 10.42.0.1.53
```

Significa:

```text
client:porta_temporanea -> gateway:porta_DNS
```

Esempio di risposta:

```text
10.42.0.1.53 > 10.42.0.x.55405
```

Significa:

```text
gateway:porta_DNS -> client:stessa_porta_temporanea
```

Il gateway `10.42.0.1` riceve la domanda DNS dal client, ottiene o recupera la risposta e la restituisce alla porta temporanea che aveva originato la richiesta.

### 6.2 Identificativo della transazione

Numeri come:

```text
35583
60270
28287
```

sono identificativi DNS. La risposta riporta lo stesso identificativo della domanda corrispondente, permettendo al client di abbinarle anche quando esistono più interrogazioni contemporanee.

Il simbolo `+` dopo l'identificativo indica che nella richiesta è impostato il bit `RD`, cioè `Recursion Desired`: il client chiede al resolver di completare la ricerca per suo conto.

### 6.3 Tipi di record osservati

`A?` richiede uno o più indirizzi IPv4:

```text
A 23.60.188.50
```

`AAAA` rappresenta un indirizzo IPv6:

```text
AAAA 2a01:...::...
```

`CNAME` indica che il nome richiesto è un alias di un altro nome. Possono essere presenti più alias consecutivi prima di arrivare all'indirizzo finale:

```text
nome richiesto
  -> CNAME
  -> CNAME
  -> nodo CDN
  -> indirizzo IP
```

`HTTPS?` non indica il contenuto di una pagina HTTPS. È una richiesta DNS per il record di tipo `HTTPS`, usato per pubblicare informazioni su come raggiungere in modo efficiente un servizio HTTPS. Il DNS resta distinto dalla successiva connessione TLS cifrata.

### 6.4 CDN e risposte multiple

La catena di `CNAME` osservata conduce anche a nomi appartenenti a una CDN. Una CDN distribuisce copie o punti di accesso del servizio su più sistemi e può restituire indirizzi differenti in base alla rete, alla posizione approssimativa, al carico e al momento della richiesta.

La presenza di più record `A` o `AAAA` offre al dispositivo più destinazioni possibili. Non significa che il telefono stabilirà necessariamente una connessione con ognuna di esse.

### 6.5 Campi del pacchetto IP e UDP

Esempio:

```text
IP (tos 0x0, ttl 64, id 14323, offset 0, flags [none], proto UDP (17), length 60)
```

Interpretazione:

- `tos 0x0`: nessuna marcatura IP speciale osservata;
- `ttl 64`: limite iniziale o residuo dei passaggi attraverso router;
- `id`: identificativo IPv4 usato anche per la frammentazione;
- `offset 0`: il frammento, se presente, comincerebbe dall'inizio;
- `flags [DF]`: `Don't Fragment`, il pacchetto non deve essere frammentato;
- `proto UDP (17)`: il protocollo trasportato da IPv4 è UDP, numero 17;
- `length`: lunghezza totale del pacchetto IPv4.

La dicitura:

```text
[udp sum ok]
```

indica che il checksum UDP verificato durante la cattura risulta corretto.

### 6.6 Considerazione sulla privacy

Il DNS tradizionale ha reso visibili nomi come domini Apple e iCloud. Questo dimostra che, anche quando il traffico applicativo è cifrato, una cattura DNS può rivelare i servizi contattati o interrogati dal dispositivo.

Una query DNS non dimostra però che l'utente abbia aperto volontariamente quel servizio: può essere stata generata automaticamente dal sistema operativo o da un'applicazione in background.

## 7. Risultati parziali

- [x] tcpdump installato e funzionante;
- [x] interfaccia hotspot identificata;
- [x] uplink identificato;
- [x] client autorizzato identificato;
- [x] cattura limitata a cinque pacchetti;
- [x] traffico in uscita e risposte osservati;
- [x] UDP 443 compatibile con QUIC riconosciuto;
- [x] TCP RST/ACK riconosciuto;
- [x] proprietario amministrativo di un blocco IP verificato tramite WHOIS;
- [x] richiesta e risposta DNS tradizionale osservate;
- [x] record DNS `A`, `AAAA`, `CNAME` e `HTTPS` riconosciuti;
- [x] assenza di pacchetti persi dal kernel verificata;
- [ ] ping ICMP osservato;
- [ ] handshake TCP completo osservato;
- [ ] stesso flusso confrontato prima e dopo il NAT;
- [ ] PCAP controllato salvato e revisionato.

## 8. Privacy

Non pubblicare:

- indirizzi MAC reali;
- nome completo dell'interfaccia Realtek;
- PCAP grezzi;
- log integrali non revisionati;
- hostname, query DNS o dati applicativi sensibili non necessari;
- informazioni che possano identificare il dispositivo o il proprietario.
