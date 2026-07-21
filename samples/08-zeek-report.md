# Report pubblico — Fase 8: Zeek e log di rete

## Stato

```text
COMPLETATA E VERIFICATA — 21 luglio 2026
```

Zeek è stato installato direttamente sul gateway Ubuntu, configurato come sensore standalone e verificato sia con una cattura manuale sia tramite ZeekControl.

## Ambiente anonimizzato

```text
Sistema:       Ubuntu 26.04 LTS
Architettura:  amd64
LAB_SUBNET:    10.42.0.0/24
GATEWAY_IP:    10.42.0.1
AP_IF:         wlx<REDACTED>
UPLINK_IF:     wlp13s0
NTP:           sincronizzato
Spazio libero: circa 739 GiB
```

Il nome completo dell’interfaccia hotspot non viene pubblicato perché incorpora un indirizzo MAC.

## Installazione

I repository Ubuntu già configurati non offrivano un pacchetto candidato. È stato aggiunto il repository ufficiale Zeek per Ubuntu 26.04 usando una chiave dedicata con `signed-by`.

```text
Zeek:         8.0.9
ZeekControl:  2.6.0-31
Prefisso:     /opt/zeek
```

Sono stati verificati i plugin di cattura `AF_Packet` e `Pcap` e gli analizzatori DNS, HTTP, TLS, QUIC e X.509.

## Cattura manuale

Comando anonimizzato:

```bash
sudo /opt/zeek/bin/zeek \
    -C \
    -i "$AP_IF" \
    -e 'Site::local_nets += { 10.42.0.0/24 };' \
    local \
    policy/tuning/json-logs
```

Risultati:

```text
pacchetti ricevuti:       12850
pacchetti kernel persi:   0
pacchetti non elaborati:  4 (0,03%)
gap TCP stimati:          0
perdita TCP stimata:      0,0%
connessioni con gap:      0
byte mancanti:            0
```

Eventi principali:

```text
conn.log    56
dns.log     67
ssl.log     32
quic.log    20
```

Tutti i log controllati erano JSON validi. `reporter.log` conteneva soltanto messaggi informativi.

## Configurazione ZeekControl

`node.cfg`:

```ini
[zeek]
type=standalone
host=localhost
interface=wlx<REDACTED>
```

`networks.cfg`:

```text
10.42.0.0/24    Rete laboratorio autorizzata
```

`zeekctl.cfg`:

```ini
PrivateAddressSpaceIsLocal = 0
LogRotationInterval = 3600
LogExpireInterval = 0
```

In `local.zeek` il `digest_salt` predefinito è stato sostituito con un valore casuale non pubblicato ed è stato abilitato il formato JSON:

```zeek
@load policy/tuning/json-logs
```

Controllo:

```bash
sudo /opt/zeek/bin/zeekctl check
```

Risultato:

```text
zeek scripts are ok.
```

## Avvio gestito

Per isolare la prova, Suricata è stato fermato temporaneamente e Zeek è stato avviato tramite ZeekControl:

```bash
sudo systemctl stop suricata
sudo /opt/zeek/bin/zeekctl deploy
sudo /opt/zeek/bin/zeekctl status
```

Stato durante la prova:

```text
zeek  standalone  localhost  running
```

Log principali osservati:

```text
conn.log    19 eventi
dns.log     85 eventi
ssl.log     13 eventi
quic.log    13 eventi
```

Tutti i file erano JSON validi.

## Arresto e ripristino

```bash
sudo /opt/zeek/bin/zeekctl stop
sudo systemctl start suricata
```

Stato finale:

```text
Zeek:      stopped
Suricata:  active
```

L’arresto di Zeek non ha interrotto hotspot, routing, NAT o accesso Internet.

## Rotazione

La configurazione prevede una rotazione ogni ora. Non è stata attesa un’ora completa; è stata però verificata l’archiviazione gestita dei log all’arresto e la lettura dei file compressi `.log.gz`.

## Problema documentato

Una redirezione come:

```bash
sudo wc -l < file.log
```

può fallire perché la shell apre il file prima di eseguire `sudo`. Forme corrette:

```bash
sudo wc -l file.log
sudo cat file.log | wc -l
sudo gzip -cd file.log.gz | wc -l
```

## Modalità operativa

```text
normalmente:             Zeek spento
sessione di laboratorio: zeekctl deploy
fine laboratorio:        zeekctl stop
avvio al boot:            non configurato
```

## Privacy

Non sono pubblicati:

- nome completo dell’interfaccia USB;
- indirizzi MAC;
- IP completi dei client;
- query e risposte DNS;
- server name TLS e certificati;
- valore di `digest_salt`;
- log integrali e backup locali.

Il materiale completo resta nel report privato locale:

```text
reports/08-zeek-private.md
```

## Prossimo passo

Fase 9: leggere i log JSON di Zeek con un programma Python commentato, senza modificare la rete.
