# Fase 6 — PCAP controllato e verifica AppArmor

**Data:** 18 luglio 2026  
**Esito:** completato

## Obiettivo

Salvare una cattura molto piccola e filtrata senza pubblicare il file grezzo, limitando il numero di pacchetti e i byte conservati per ciascun pacchetto.

## Parametri della cattura

```text
interfacce: tutte (`any`)
filtro: client o uplink, UDP porta 443
limite: 20 pacchetti
snapshot length: 128 byte
formato: PCAP 2.4, Linux cooked v2
posizione: cartella privata esterna al repository
```

Il PCAP è stato prodotto tramite una pipe, così `tcpdump` ha scritto sullo standard output e un processo eseguito dall'utente ha creato il file:

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

## File verificato

```text
proprietario: utente del laboratorio
gruppo: gruppo principale dell'host
permessi finali: 600
dimensione: circa 2,8 KiB
riconoscimento: pcap capture file, microsecond timestamps
capture length: 128
```

Il file non viene inserito nel repository.

## AppArmor

La lettura diretta ha restituito `Permission denied` anche con `sudo`. Il journal del kernel ha confermato che il profilo AppArmor `tcpdump` ha negato:

```text
operation="mknod" profile="tcpdump" requested_mask="c"
operation="open"  profile="tcpdump" requested_mask="r"
capname="dac_read_search"
```

Il profilo è risultato attivo:

```bash
sudo aa-status | grep -i tcpdump
```

Non è stato disabilitato né modificato.

## Lettura compatibile con AppArmor

Il file è stato aperto dalla shell e passato a `tcpdump` tramite standard input:

```bash
tcpdump -nn -tttt -r - < "$PCAP_FILE"
```

Estratto anonimizzato:

```text
wlx<REDACTED> In  IP 10.42.0.x.PORTA > IP_REMOTO.443: UDP, length 1350
wlp13s0 Out       IP 192.168.10.x.PORTA > IP_REMOTO.443: UDP, length 1350
wlp13s0 In        IP IP_REMOTO.443 > 192.168.10.x.PORTA: UDP, length 1200
wlx<REDACTED> Out IP IP_REMOTO.443 > 10.42.0.x.PORTA: UDP, length 1200
```

Il PCAP conferma nuovamente:

```text
client privato -> NAT -> uplink -> Internet
Internet -> uplink -> traduzione inversa -> client privato
```

## Nota sullo snapshot

L'opzione `-s 128` limita i byte materialmente salvati per ciascun record. `tcpdump`, durante la lettura, può comunque mostrare la lunghezza originale dichiarata nell'intestazione del pacchetto, per esempio `UDP, length 1350`. Questo non significa che tutti quei byte siano stati conservati nel PCAP.

## Conclusione

- PCAP limitato creato correttamente;
- permessi privati applicati;
- formato verificato;
- lettura completata senza disabilitare AppArmor;
- NAT riconosciuto anche nel file salvato;
- PCAP grezzo mantenuto fuori dal repository.
