# Fase 6 — Confronto tcpdump prima e dopo il NAT

**Data del test:** 18 luglio 2026  
**Stato:** **VERIFICATO**

Questo documento integra il report della fase 6 con una cattura simultanea sulle interfacce del gateway. I nomi completi delle interfacce e gli indirizzi locali completi sono anonimizzati.

## 1. Obiettivo

Dimostrare che lo stesso flusso attraversa il gateway in due forme:

```text
prima del NAT: client 10.42.0.x -> server Internet
dopo il NAT:  gateway 192.168.10.x -> server Internet
```

La risposta deve mostrare la trasformazione inversa:

```text
prima del DNAT/conntrack di ritorno: server -> gateway 192.168.10.x
dopo la traduzione di ritorno:      server -> client 10.42.0.x
```

## 2. Comando usato

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

Opzioni principali:

- `-i any`: osserva tutte le interfacce Linux contemporaneamente;
- `-nn`: non risolve né indirizzi né porte in nomi;
- `-tttt`: mostra data e ora complete;
- `-vv`: mostra dettagli aggiuntivi dei pacchetti;
- `-c 80`: termina dopo ottanta pacchetti catturati.

Il messaggio seguente è normale con `-i any`:

```text
WARNING: any: That device doesn't support promiscuous mode
Promiscuous mode not supported on the "any" device
```

L'interfaccia virtuale `any` usa il formato Linux cooked capture e non richiede la modalità promiscua per osservare il traffico consegnato allo stack di rete del gateway.

## 3. Flusso in uscita osservato

Estratto anonimizzato:

```text
wlx<REDACTED> In
10.42.0.x.57336 > 31.13.86.52.443: UDP, length 68

wlp13s0 Out
192.168.10.x.57336 > 31.13.86.52.443: UDP, length 68
```

Le due righe descrivono lo stesso datagramma:

```text
IP remoto:          31.13.86.52
porta client:       57336
porta server:       443
protocollo:         UDP
payload UDP:        68 byte
```

La differenza importante è l'indirizzo sorgente:

```text
lato hotspot: 10.42.0.x
lato uplink:  192.168.10.x
```

Il NAT ha quindi sostituito l'indirizzo privato del client con l'indirizzo dell'uplink del gateway. In questo flusso la porta sorgente è rimasta invariata, ma il NAT potrebbe cambiarla in caso di collisioni o altre esigenze di conntrack.

## 4. Flusso di risposta osservato

Estratto anonimizzato:

```text
wlp13s0 In
31.13.86.52.443 > 192.168.10.x.57336: UDP, length 80

wlx<REDACTED> Out
31.13.86.52.443 > 10.42.0.x.57336: UDP, length 80
```

La risposta arriva prima all'indirizzo uplink del gateway. Il sistema consulta lo stato della connessione e ripristina la destinazione originale del client prima di inoltrarla sulla rete hotspot.

## 5. Prova tramite TTL

Nel flusso in uscita è stato osservato:

```text
hotspot In: ttl 64
uplink Out: ttl 63
```

Nel flusso di ritorno:

```text
uplink In:  ttl 82
hotspot Out: ttl 81
```

Il decremento di uno conferma che Ubuntu sta inoltrando il pacchetto come router. Il NAT modifica gli indirizzi, mentre il forwarding IPv4 decrementa il TTL.

## 6. Altri flussi accoppiati

La stessa trasformazione è stata osservata verso più server remoti, per esempio:

```text
10.42.0.x:49741  -> 157.240.231.63:443
192.168.10.x:49741 -> 157.240.231.63:443

10.42.0.x:59270  -> 163.70.128.63:443
192.168.10.x:59270 -> 163.70.128.63:443

10.42.0.x:55265  -> 17.248.250.20:443
192.168.10.x:55265 -> 17.248.250.20:443

10.42.0.x:57490  -> 172.224.98.8:443
192.168.10.x:57490 -> 172.224.98.8:443
```

Sono stati osservati prevalentemente datagrammi UDP sulla porta 443, compatibili con traffico QUIC/HTTP3 cifrato.

## 7. Traffico del gateway distinto da quello inoltrato

Il filtro includeva sia l'IP del client sia l'IP dell'uplink. Per questo sono comparsi anche flussi visibili soltanto su `wlp13s0`, per esempio:

```text
192.168.10.x:60002 <-> 104.18.32.47:443
```

Quando non esiste una riga quasi simultanea sulla Realtek con sorgente o destinazione `10.42.0.x`, quel traffico può essere stato generato direttamente dal gateway Ubuntu, anziché essere stato inoltrato dal telefono.

Per riconoscere con sicurezza un flusso NAT bisogna cercare una coppia con:

- stesso IP remoto;
- stesso protocollo;
- stesse porte, salvo eventuale traduzione della porta;
- stessa lunghezza;
- timestamp quasi identico;
- una riga sulla Realtek e una sulla MediaTek.

## 8. Statistiche

```text
80 packets captured
111 packets received by filter
0 packets dropped by kernel
```

Il limite di ottanta pacchetti ha terminato la cattura. Più pacchetti erano già stati consegnati al filtro durante l'arresto, ma nessun pacchetto risulta perso dal kernel.

## 9. Conclusione

Il percorso è stato verificato:

```text
client 10.42.0.x
    -> Realtek In
    -> forwarding e NAT sul gateway
    -> MediaTek Out come 192.168.10.x
    -> Internet

Internet
    -> MediaTek In verso 192.168.10.x
    -> conntrack e traduzione inversa
    -> Realtek Out verso 10.42.0.x
```

Risultati:

- [x] stesso flusso osservato sui due lati del gateway;
- [x] sostituzione dell'IP sorgente verificata;
- [x] traduzione inversa delle risposte verificata;
- [x] decremento TTL durante il forwarding verificato;
- [x] traffico inoltrato distinto dal possibile traffico locale del gateway;
- [x] nessun pacchetto perso dal kernel.