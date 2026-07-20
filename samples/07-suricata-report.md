# Fase 7 — Report pubblico Suricata IDS

## Stato

```text
COMPLETATA E VERIFICATA — 20 luglio 2026
```

## Obiettivo

Installare Suricata direttamente sul gateway Ubuntu, osservare in modalità IDS passiva il traffico della rete di laboratorio autorizzata e produrre log JSON utilizzabili nelle successive analisi Python.

## Architettura verificata

```text
client autorizzato
        |
        v
hotspot Realtek — 10.42.0.0/24
        |
        +--> Suricata AF_PACKET, IDS passivo
        |
        v
nftables -> routing -> NAT -> uplink -> Internet
```

Suricata è installato sull’host Ubuntu, non in Docker. Docker sarà usato successivamente per importazione dati, database, API e dashboard.

## Ambiente anonimizzato

```text
Sistema:       Ubuntu 26.04 LTS
Kernel:        7.0.0-27-generic
Suricata:      8.0.3 RELEASE
AP_IF:         wlx<REDACTED>
UPLINK_IF:     wlp13s0
LAB_SUBNET:    10.42.0.0/24
GATEWAY_IP:    10.42.0.1
```

## Funzionalità verificate

La build installata supporta:

```text
AF_PACKET
AF_XDP
NFQueue
Hyperscan
Rust
systemd
Python
```

Per la fase è stato usato AF_PACKET.

## Problemi incontrati

### Interfaccia predefinita inesistente

La configurazione iniziale indicava:

```yaml
af-packet:
  - interface: eth0
```

Il gateway non possiede `eth0`. Il servizio falliva con:

```text
af-packet: eth0: failed to find interface
failed to init socket for interface
```

La configurazione è stata corretta usando l’interfaccia hotspot reale, anonimizzata in questo report.

### Regole mancanti

Il primo avvio non trovava:

```text
/var/lib/suricata/rules/suricata.rules
```

Le regole sono state installate tramite `suricata-update`.

## Configurazione finale

```yaml
HOME_NET: "[10.42.0.0/24]"

af-packet:
  - interface: wlx<REDACTED>

rule-files:
  - suricata.rules
  - local.rules
```

La configurazione è stata verificata con:

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml
```

Risultato:

```text
Configuration provided was successfully loaded. Exiting.
Codice di uscita: 0
```

## Regole caricate

Con la regola locale attiva:

```text
2 file di regole
52044 regole caricate
0 regole fallite
0 regole saltate
52049 firme elaborate
```

## Eventi reali osservati

Durante una breve prova autorizzata sono stati osservati:

```text
flow
quic
mdns
dns
tls
http
fileinfo
dhcp
stats
alert
```

La maggior parte del traffico web era cifrata e classificata come TLS o QUIC.

## Alert decoder

È stato osservato un alert generico:

```text
SURICATA Ethertype unknown
SID 2200121
severità 3
action allowed
```

L’evento riguardava un frame Ethernet broadcast senza campi IP. È documentato come anomalia di decodifica o protocollo locale, non come prova di attacco.

## Regola locale di test

È stata aggiunta una regola innocua e ripetibile:

```text
alert icmp $HOME_NET any -> $HOME_NET any (msg:"LAB Suricata ICMP test"; itype:8; sid:1000001; rev:1;)
```

Un singolo ICMP Echo Request broadcast ha generato:

```text
signature: LAB Suricata ICMP test
proto:     ICMP
source:    gateway laboratorio
destination: broadcast laboratorio
action:    allowed
```

`allowed` conferma che Suricata osserva e segnala senza bloccare.

## Avvio su richiesta

Suricata non parte automaticamente con Ubuntu.

Durante la prova:

```text
is-active:  active
is-enabled: disabled
```

Dopo l’arresto:

```text
is-active:  inactive
is-enabled: disabled
```

Comandi operativi:

```bash
sudo systemctl start suricata
sudo systemctl stop suricata
```

L’arresto di Suricata non interrompe hotspot, routing, NAT o Internet.

## Statistiche di cattura

Prova systemd di circa 62 secondi:

```text
pacchetti finali: 145724
drop finali:      367
drop percentuale: 0.25%
checksum invalidi: 0
alert:             1
```

Non sono stati osservati errori AF_PACKET di polling o invio. Non è stato applicato tuning preventivo.

## Log prodotti

```text
eve.json
fast.log
stats.log
suricata.log
```

`eve.json` contiene eventi JSON strutturati e sarà usato nelle fasi Python e Docker.

## Rotazione dei log

Politica verificata:

```text
controllo:       giornaliero tramite logrotate.timer
soglia:          1 MiB
copie:           14
compressione:    gzip
metodo:          copytruncate
```

Il blocco `postrotate` invia HUP soltanto se `suricata.service` è attivo.

La rotazione reale di `eve.json` ha creato:

```text
eve.json       nuovo file corrente
eve.json.1.gz  archivio compresso, circa 115 KiB
```

Durante e dopo la rotazione Suricata era `inactive` e `disabled`.

## Privacy

Non sono pubblicati:

- nome completo dell’interfaccia USB;
- indirizzi MAC;
- hostname e percorsi personali;
- query DNS reali;
- log integrali;
- frame Ethernet grezzi;
- file `eve.json` completo.

## Risultato finale

- Suricata installato sull’host Ubuntu;
- modalità IDS passiva verificata;
- AF_PACKET configurato sull’hotspot;
- `HOME_NET` limitato alla rete laboratorio;
- regole caricate senza errori;
- eventi reali prodotti;
- alert locale controllato verificato;
- avvio e arresto on demand verificati;
- avvio automatico disabilitato;
- drop misurati e documentati;
- rotazione e compressione dei log verificate.

## Prossimo passo

Installare Zeek e confrontare i suoi log strutturati con gli eventi Suricata.
