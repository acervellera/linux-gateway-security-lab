# Fase 7 — Suricata IDS

## Stato

```text
COMPLETATA E VERIFICATA — 20 luglio 2026
```

Suricata è stato installato e configurato sull’host Ubuntu gateway in modalità IDS passiva. Sono stati verificati cattura AF_PACKET, regole, log JSON, avvio e arresto su richiesta, alert controllato e rotazione reale dei log.

Suricata resta disabilitato all’avvio del sistema e viene attivato soltanto durante le sessioni di laboratorio.

## Obiettivo raggiunto

Il gateway osserva il traffico della rete autorizzata `10.42.0.0/24` e produce eventi strutturati utilizzabili successivamente da Python.

```text
client autorizzato
        |
        v
hotspot Realtek
        |
        +--> Suricata IDS passivo
        |
        v
nftables, routing, NAT e uplink
```

Suricata:

```text
osserva -> analizza -> registra -> avvisa
```

Non blocca automaticamente il traffico. Gli alert verificati hanno azione `allowed`.

## Collocazione architetturale

Suricata è installato direttamente sull’host Ubuntu, non in Docker.

```text
Ubuntu host
    hotspot, DHCP, routing, firewall, Suricata e Zeek

Docker
    importazione dati, database, API e dashboard
```

Questa separazione permette l’accesso diretto all’interfaccia fisica tramite AF_PACKET senza usare container privilegiati o `network_mode: host`.

## Ambiente anonimizzato

```text
Sistema:       Ubuntu 26.04 LTS
Kernel:        7.0.0-27-generic
Architettura:  x86_64
LAB_SUBNET:    10.42.0.0/24
GATEWAY_IP:    10.42.0.1
AP_IF:         wlx<REDACTED>
UPLINK_IF:     wlp13s0
Orologio:      sincronizzato tramite NTP
Spazio libero: circa 741 GiB
```

Il nome completo dell’interfaccia USB, che incorpora un indirizzo MAC, resta soltanto nel report privato locale.

## Pacchetti installati

Sono stati usati i repository Ubuntu già configurati, senza PPA esterni.

```text
Suricata:         8.0.3 RELEASE
suricata-update:  1.3.7
jq:               1.8.1
```

Comandi principali:

```bash
sudo apt update
sudo apt install suricata suricata-update jq
```

Sulla versione installata il comando corretto per la versione è:

```bash
suricata -V
```

`suricata --version` non è riconosciuto.

## Funzionalità della build

Il comando:

```bash
suricata --build-info
```

ha confermato:

```text
AF_PACKET support:  yes
AF_XDP support:     yes
NFQueue support:    yes
Detection enabled:  yes
Hyperscan support:  yes
Rust presente:      yes
Systemd support:    yes
Python support:     yes
```

Per questa fase è stata scelta la cattura AF_PACKET.

## Primo avvio fallito e diagnosi

Durante l’installazione il servizio ha tentato di usare la configurazione predefinita:

```yaml
af-packet:
  - interface: eth0
```

Sul gateway non esiste `eth0`. Il log ha quindi mostrato:

```text
af-packet: eth0: failed to find interface: No such device
af-packet: eth0: failed to init socket for interface
thread "W#01-eth0" failed to start
```

Systemd ha riprovato più volte e ha marcato il servizio come `failed`.

La causa era esclusivamente il nome errato dell’interfaccia nella configurazione predefinita; routing, firewall e hotspot non erano coinvolti.

## Regole inizialmente mancanti

Il primo tentativo mostrava anche:

```text
No rule files match the pattern /var/lib/suricata/rules/suricata.rules
1 rule files specified, but no rules were loaded
```

Le regole sono state installate con:

```bash
sudo suricata-update
```

File verificato:

```text
/var/lib/suricata/rules/suricata.rules
dimensione osservata: circa 43 MiB
```

Con la regola locale attiva, il test finale ha elaborato:

```text
2 file di regole
52044 regole caricate correttamente
0 regole fallite
0 regole saltate
52049 firme elaborate
```

Ripartizione osservata:

```text
1303 firme IP-only
4506 firme che ispezionano il payload
46003 firme applicative
110 eventi decoder
```

## Backup e configurazione

Prima delle modifiche sono stati creati backup con `cp -a`, preservando permessi, proprietario e timestamp.

### HOME_NET

Valore originale:

```yaml
HOME_NET: "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]"
```

Valore verificato:

```yaml
HOME_NET: "[10.42.0.0/24]"
```

In questo modo soltanto la subnet autorizzata del laboratorio viene considerata interna.

### Interfaccia AF_PACKET

Valore originale:

```yaml
af-packet:
  - interface: eth0
```

Valore locale verificato:

```yaml
af-packet:
  - interface: wlx<REDACTED>
```

La modifica è stata applicata con uno script Python prudente che:

- legge il file tramite `pathlib.Path`;
- individua la sezione `af-packet`;
- sostituisce solo la riga prevista;
- verifica che `HOME_NET` corrisponda alla struttura attesa;
- interrompe l’operazione in caso di ambiguità;
- scrive il file soltanto dopo tutti i controlli.

Un primo script più semplice si era fermato correttamente perché nel file erano presenti tre riferimenti a `eth0`. Nessuna sostituzione indiscriminata è stata applicata.

## Verifica della configurazione

Comando:

```bash
sudo suricata \
    -T \
    -c /etc/suricata/suricata.yaml
```

Risultato:

```text
Configuration provided was successfully loaded. Exiting.
Codice di uscita: 0
```

Il test ha verificato sintassi YAML, variabili di rete, file delle regole e caricamento delle firme.

## Prima esecuzione in primo piano

Suricata è stato eseguito senza demone:

```bash
sudo suricata \
    --af-packet \
    -c /etc/suricata/suricata.yaml \
    -l /var/log/suricata \
    -v
```

Il log ha confermato:

```text
interfaccia corretta rilevata
MTU 1500
12 thread di cattura creati
Engine started
```

La prova è stata terminata con `Ctrl+C`:

```text
Signal Received. Stopping engine.
time elapsed 35.857s
```

Dopo l’arresto non risultavano processi Suricata attivi.

## Eventi osservati in eve.json

Durante una prova con client autorizzato sono stati osservati:

```text
45 flow
38 quic
37 mdns
24 dns
15 tls
5 stats
1 http
1 fileinfo
1 dhcp
1 alert
```

Interpretazione:

- `flow`: connessioni e flussi;
- `quic`: traffico cifrato moderno, normalmente UDP/443;
- `mdns`: scoperta locale di dispositivi e servizi;
- `dns`: domande e risposte DNS;
- `tls`: sessioni HTTPS cifrate;
- `http`: traffico HTTP non cifrato;
- `fileinfo`: metadati di contenuti osservati;
- `dhcp`: configurazione di rete del client;
- `stats`: statistiche interne;
- `alert`: evento attivato da una firma.

La predominanza di TLS e QUIC rispetto a HTTP è coerente con il traffico web moderno.

## Alert decoder osservato

Durante la prima prova è comparso:

```text
Signature:   SURICATA Ethertype unknown
SID:         2200121
Categoria:   Generic Protocol Command Decode
Severità:    3
Azione:      allowed
Interfaccia: AP_IF
```

I campi IP e porte erano assenti perché l’evento riguardava un frame Ethernet broadcast non classificato prima dell’analisi IP.

L’evento è documentato come anomalia di decodifica o protocollo locale, non come prova di attacco. Non è stata applicata suppression.

## Modalità operativa scelta

Suricata non resta sempre attivo.

```text
normalmente:            spento
durante il laboratorio: avvio manuale
fine laboratorio:       arresto controllato
avvio al boot:          disabilitato
```

Comandi:

```bash
sudo systemctl start suricata
sudo systemctl stop suricata
```

La prova reale ha confermato durante l’esecuzione:

```text
systemctl is-active suricata  -> active
systemctl is-enabled suricata -> disabled
```

Dopo l’arresto:

```text
systemctl is-active suricata  -> inactive
systemctl is-enabled suricata -> disabled
```

Fermare Suricata non interrompe hotspot, routing, NAT o accesso Internet.

## Regola locale controllata

È stato creato:

```text
/var/lib/suricata/rules/local.rules
```

Regola:

```text
alert icmp $HOME_NET any -> $HOME_NET any (msg:"LAB Suricata ICMP test"; itype:8; sid:1000001; rev:1;)
```

Significato:

- `alert`: genera un avviso senza bloccare;
- `icmp`: limita la regola a ICMP;
- `$HOME_NET -> $HOME_NET`: traffico interno al laboratorio;
- `itype:8`: ICMP Echo Request;
- `sid:1000001`: identificatore locale;
- `rev:1`: prima revisione.

La configurazione carica:

```yaml
rule-files:
  - suricata.rules
  - local.rules
```

## Alert intenzionale e ripetibile

È stato inviato un solo ping broadcast nella rete del laboratorio:

```bash
sudo ping \
    -b \
    -c 1 \
    -I "$AP_IF" \
    10.42.0.255
```

L’assenza di risposte era prevista e non rappresentava un errore.

`fast.log` ha registrato:

```text
[1:1000001:1] LAB Suricata ICMP test
{ICMP} 10.42.0.1 -> 10.42.0.255
```

Estratto anonimizzato di `eve.json`:

```json
{
  "event_type": "alert",
  "proto": "ICMP",
  "signature": "LAB Suricata ICMP test",
  "signature_id": 1000001,
  "severity": 3,
  "action": "allowed"
}
```

`allowed` conferma che Suricata è rimasto in modalità IDS passiva.

## Statistiche della prova systemd

La sessione con regola locale è durata circa 62 secondi.

Ultimo evento periodico `stats`:

```text
kernel_packets:  145344
kernel_drops:    9
errors:          0
decoder_packets: 145331
alerts:          1
poll_errors:     0
send_errors:     0
```

Riepilogo AF_PACKET alla chiusura:

```text
packets:          145724
drops:            367
drop percentage:  0.25%
invalid checksum: 0
alerts:           1
```

La differenza dipende dal momento in cui viene emesso l’evento periodico rispetto al riepilogo finale. La perdita finale dello `0,25%` è stata registrata e non è stata considerata anomala per questa prova breve; non è stato applicato tuning preventivo.

## Log prodotti

```text
/var/log/suricata/eve.json
/var/log/suricata/fast.log
/var/log/suricata/stats.log
/var/log/suricata/suricata.log
```

- `eve.json`: eventi JSON strutturati;
- `fast.log`: riepilogo testuale degli alert;
- `stats.log`: statistiche del motore;
- `suricata.log`: messaggi operativi.

## Rotazione dei log

Il pacchetto Ubuntu ha installato:

```text
/etc/logrotate.d/suricata
```

La politica verificata è:

```text
controllo:       giornaliero tramite logrotate.timer
soglia:          1 MiB per file
copie:           14
compressione:    gzip
metodo:          copytruncate
file:            /var/log/suricata/*.log e *.json
```

La configurazione globale contiene `weekly`, ma la regola Suricata usa una soglia di dimensione. Il timer systemd esegue il controllo giornalmente e ruota soltanto i file che superano 1 MiB.

### Postrotate compatibile con uso on demand

Il blocco originale tentava di leggere il PID anche con Suricata spento. È stato sostituito con:

```conf
postrotate
    if /usr/bin/systemctl --quiet is-active suricata.service; then
        /usr/bin/systemctl kill --signal=HUP --kill-who=main suricata.service
    fi
endscript
```

Il segnale HUP viene quindi inviato soltanto se il servizio è attivo.

### Rotazione reale verificata

Con Suricata fermo, `logrotate -v` ha ruotato `eve.json` perché aveva superato 1 MiB.

Risultato:

```text
eve.json       nuovo file corrente, 0 byte
eve.json.1.gz  archivio compresso, circa 115 KiB
Suricata       inactive
avvio al boot  disabled
```

La simulazione precedente con `logrotate -d` non aveva modificato i file.

## Comandi operativi

### Avvio della sessione

```bash
sudo nmcli connection up security-gateway-ap
sudo systemctl start suricata
systemctl is-active suricata
systemctl is-enabled suricata
```

Risultato atteso:

```text
active
disabled
```

### Fine della sessione

```bash
sudo systemctl stop suricata
systemctl is-active suricata
systemctl is-enabled suricata
```

Risultato atteso:

```text
inactive
disabled
```

### Controllo eventi

```bash
sudo jq -r '.event_type' \
    /var/log/suricata/eve.json |
    sort |
    uniq -c |
    sort -nr
```

### Controllo alert

```bash
sudo tail -n 30 /var/log/suricata/fast.log
```

### Controllo configurazione

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml
```

## Attività completate

- [x] installazione di Suricata, `suricata-update` e `jq`;
- [x] registrazione di versione e funzionalità;
- [x] installazione sull’host e non in Docker;
- [x] scelta di AF_PACKET;
- [x] diagnosi dell’errore `eth0`;
- [x] backup della configurazione;
- [x] configurazione di `HOME_NET`;
- [x] configurazione dell’interfaccia hotspot;
- [x] installazione e verifica delle regole;
- [x] test della configurazione con codice `0`;
- [x] cattura manuale in primo piano;
- [x] osservazione di traffico reale autorizzato;
- [x] lettura di `fast.log`, `eve.json` e `suricata.log`;
- [x] avvio e arresto su richiesta tramite systemd;
- [x] conferma `active/disabled`;
- [x] regola locale innocua;
- [x] alert intenzionale e ripetibile;
- [x] controllo di errori e pacchetti persi;
- [x] rotazione reale di `eve.json`;
- [x] conservazione di 14 archivi compressi;
- [x] arresto senza interrompere routing e hotspot;
- [x] report pubblico anonimizzato;
- [x] report privato preparato fuori da Git.

## Privacy

Non pubblicare:

- nome completo dell’interfaccia USB che incorpora il MAC;
- indirizzi MAC;
- frame Ethernet grezzi;
- query DNS personali;
- hostname e percorsi locali;
- log integrali;
- file `eve.json` completi;
- indirizzi e porte reali non necessari.

## File prodotti

Report pubblico:

```text
samples/07-suricata-report.md
```

Report privato locale:

```text
reports/07-suricata-private.md
```

Il report privato deve restare escluso da Git.

## Rollback

Arrestare e disabilitare:

```bash
sudo systemctl stop suricata
sudo systemctl disable suricata
```

Ripristinare un backup della configurazione:

```bash
sudo cp -a \
    /etc/suricata/suricata.yaml.backup-<TIMESTAMP> \
    /etc/suricata/suricata.yaml
```

Ripristinare logrotate, se necessario:

```bash
sudo cp -a \
    /etc/logrotate.d/suricata.backup-<TIMESTAMP> \
    /etc/logrotate.d/suricata
```

Verificare:

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml
```

## Condizione di completamento

- Suricata parte senza errori;
- osserva l’interfaccia hotspot;
- produce `eve.json`;
- registra un alert controllato;
- usa la modalità IDS passiva;
- resta disabilitato al boot;
- può essere arrestato senza interrompere il gateway;
- i log vengono ruotati e compressi;
- report pubblico e privato sono preparati.

## Prossimo passo

Fase 8: installare Zeek sull’host Ubuntu e confrontare i suoi log di rete con gli eventi Suricata.
