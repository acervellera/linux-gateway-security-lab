# Fase 7 — Suricata IDS

## Stato

```text
IN CORSO — installazione, configurazione e cattura manuale verificate il 18 luglio 2026
```

La prova di avvio e arresto tramite `systemd` su richiesta non è stata ancora eseguita. Suricata non deve essere abilitato automaticamente all'avvio del gateway.

## Obiettivo

Installare Suricata sul gateway Ubuntu, osservare il traffico del laboratorio in modalità IDS passiva e produrre avvisi e log JSON utilizzabili successivamente da Python.

## Ruolo di Suricata

Suricata è un motore IDS/IPS e di monitoraggio di rete. In questa fase è usato come IDS passivo:

```text
osserva -> analizza -> registra -> avvisa
```

Non blocca automaticamente il traffico. Gli eventi rilevati durante questa fase hanno quindi azione `allowed`.

## Collocazione architetturale

Suricata è installato direttamente sull'host Ubuntu gateway, non in Docker.

```text
Ubuntu host
    hotspot, DHCP, routing, firewall, Suricata e Zeek

Docker
    importazione dati, database, API e dashboard
```

Questa separazione permette a Suricata di osservare direttamente l'interfaccia fisica tramite AF_PACKET senza usare container privilegiati o `network_mode: host`.

## Ambiente verificato

```text
Sistema:       Ubuntu 26.04 LTS
Kernel:        7.0.0-27-generic
Architettura:  x86_64
LAB_SUBNET:    10.42.0.0/24
GATEWAY_IP:    10.42.0.1
AP_IF:         wlx<REDACTED>
UPLINK_IF:     wlp13s0
Spazio libero: circa 741 GiB
Orologio:      sincronizzato tramite NTP
```

Il nome completo dell'interfaccia hotspot resta nei dati locali e non viene pubblicato.

## Pacchetti installati

Sono stati usati i pacchetti dei repository Ubuntu configurati, senza aggiungere PPA esterni:

```text
Suricata:         8.0.3 RELEASE
suricata-update:  1.3.7
jq:               1.8.1
```

Nota: sulla versione installata l'opzione corretta per mostrare la versione è:

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

## Primo avvio automatico fallito

Durante l'installazione il pacchetto ha tentato di avviare il servizio con:

```text
/usr/bin/suricata -D --af-packet -c /etc/suricata/suricata.yaml
```

La configurazione predefinita indicava:

```yaml
af-packet:
  - interface: eth0
```

Sul gateway non esiste alcuna interfaccia `eth0`. Il log ha quindi mostrato:

```text
af-packet: eth0: failed to find interface: No such device
af-packet: eth0: failed to init socket for interface
thread "W#01-eth0" failed to start
```

Systemd ha riprovato più volte e infine ha marcato il servizio come `failed`. Il problema non riguardava routing, firewall o hotspot: era esclusivamente il nome errato dell'interfaccia nella configurazione predefinita.

## Regole inizialmente mancanti

Il primo tentativo mostrava anche:

```text
No rule files match the pattern /var/lib/suricata/rules/suricata.rules
1 rule files specified, but no rules were loaded
```

Le regole sono state successivamente installate e verificate. Il test finale ha caricato:

```text
1 file di regole elaborato
52043 regole caricate correttamente
0 regole fallite
0 regole saltate
52048 firme elaborate
```

Ripartizione osservata:

```text
1303 firme IP-only
4506 firme che ispezionano il payload
46003 firme applicative
110 eventi decoder
```

## Backup e modifica della configurazione

Prima della modifica è stato creato un backup con `cp -a`, preservando permessi, proprietario e timestamp.

Sono state cambiate soltanto due impostazioni operative.

### HOME_NET

Configurazione originale:

```yaml
HOME_NET: "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]"
```

Configurazione del laboratorio:

```yaml
HOME_NET: "[10.42.0.0/24]"
```

Questo evita di considerare interne tutte le reti private e limita `HOME_NET` alla sola subnet autorizzata del laboratorio.

### Interfaccia AF_PACKET

Configurazione originale:

```yaml
af-packet:
  - interface: eth0
```

Configurazione locale verificata:

```yaml
af-packet:
  - interface: wlx<REDACTED>
```

La modifica è stata eseguita con uno script Python prudente che:

- legge il file tramite `pathlib.Path`;
- individua la sezione `af-packet`;
- modifica soltanto la riga dell'interfaccia in quella sezione;
- controlla che `HOME_NET` sia presente una sola volta;
- interrompe l'operazione se il file non corrisponde alla struttura attesa;
- scrive il file solo dopo il superamento di tutti i controlli.

Il primo script più semplice si era fermato correttamente perché trovava tre riferimenti a `eth0` nel file. Nessuna sostituzione indiscriminata è stata applicata.

## Test della configurazione

Il comando verificato è:

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

Il test ha confermato contemporaneamente:

- sintassi YAML valida;
- `HOME_NET` valido;
- file delle regole presente;
- tutte le regole caricate senza errori;
- configurazione AF_PACKET leggibile.

## Prima esecuzione manuale

Suricata è stato eseguito in primo piano, senza demone e senza abilitazione automatica:

```bash
sudo suricata \
    --af-packet \
    -c /etc/suricata/suricata.yaml \
    -l /var/log/suricata \
    -v
```

L'interfaccia era attiva:

```text
AP_IF  UP  10.42.0.1/24
```

Il log ha confermato:

```text
interfaccia corretta rilevata
MTU 1500
12 thread di cattura creati
Engine started
```

La prova è durata circa 36 secondi ed è stata fermata in modo controllato con `Ctrl+C`:

```text
Signal Received. Stopping engine.
time elapsed 35.857s
```

Dopo l'arresto non risultavano processi Suricata attivi.

## Eventi osservati in `eve.json`

Durante la prova con un client autorizzato collegato all'hotspot sono stati registrati:

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

- `flow`: connessioni e flussi osservati;
- `quic`: traffico cifrato moderno, normalmente UDP/443;
- `mdns`: scoperta locale di dispositivi e servizi;
- `dns`: domande e risposte DNS;
- `tls`: sessioni cifrate HTTPS;
- `http`: traffico HTTP non cifrato;
- `fileinfo`: metadati di un contenuto osservato;
- `dhcp`: configurazione di rete del client;
- `stats`: statistiche interne;
- `alert`: evento attivato da una firma.

La predominanza di TLS e QUIC rispetto a HTTP è coerente con il traffico web moderno cifrato.

## Alert osservato

L'unico alert registrato è stato:

```text
Signature:  SURICATA Ethertype unknown
SID:        2200121
Categoria:  Generic Protocol Command Decode
Severità:   3
Azione:     allowed
Interfaccia: AP_IF
```

I campi IP e porte erano assenti perché l'evento riguarda un frame Ethernet non classificato prima dell'analisi IP:

```text
flow_id:   null
src_ip:    null
dest_ip:   null
proto:     null
```

Il frame era broadcast. I dati Ethernet grezzi e gli indirizzi MAC non vengono pubblicati.

Questo evento viene documentato come possibile anomalia di decodifica o protocollo locale, non come prova di attacco. Non è stato ancora applicato alcun tuning o suppression.

## Statistiche di cattura

L'ultimo evento `stats` di `eve.json` mostrava:

```text
kernel_packets:  4784
kernel_drops:    1
errors:          0
decoder_packets: 4783
poll_errors:     0
send_errors:     0
```

Il riepilogo operativo alla chiusura mostrava:

```text
packets:          4790
drops:            2
drop percentage:  0.04%
invalid checksum: 0
alerts:           1
```

La differenza tra i contatori dipende dal momento in cui sono stati registrati gli eventi `stats` rispetto alla chiusura finale. Una perdita dello `0,04%` in questa breve prova di avvio e arresto non è stata considerata anomala, ma dovrà essere ricontrollata in prove più lunghe.

## Log prodotti

Sono stati creati e letti:

```text
/var/log/suricata/eve.json
/var/log/suricata/fast.log
/var/log/suricata/stats.log
/var/log/suricata/suricata.log
```

`eve.json` contiene gli eventi JSON strutturati. `fast.log` conteneva il riepilogo testuale dell'unico alert. `suricata.log` ha documentato caricamento delle regole, avvio del motore, thread, arresto e statistiche finali.

## Rotazione dei log

Il pacchetto Ubuntu ha installato:

```text
/etc/logrotate.d/suricata
```

Configurazione osservata:

```text
rotate 14
missingok
compress
copytruncate
sharedscripts
postrotate: invio di SIGHUP a Suricata
```

`rotate 14` indica la conservazione di quattordici rotazioni. La frequenza effettiva dipende dalla configurazione globale di logrotate e deve ancora essere verificata e documentata prima di considerare completata la politica di conservazione.

## Modalità operativa scelta

Suricata non resterà sempre attivo. La modalità scelta per il laboratorio è su richiesta:

```text
normalmente:          spento
durante il laboratorio: avvio manuale
fine laboratorio:     arresto controllato
avvio al boot:        disabilitato
```

Possibili modalità:

### Primo piano, utile per studio e diagnosi

```bash
sudo suricata --af-packet -c /etc/suricata/suricata.yaml -l /var/log/suricata
```

Arresto:

```text
Ctrl+C
```

### Servizio avviato soltanto quando serve

```bash
sudo systemctl start suricata
sudo systemctl stop suricata
```

Il servizio deve restare `disabled`, così l'avvio manuale non implica l'avvio automatico al boot.

## Attività completate

- [x] installare Suricata, `suricata-update` e `jq`;
- [x] registrare versione e build info;
- [x] confermare l'installazione sull'host e non in Docker;
- [x] scegliere AF_PACKET come modalità di cattura;
- [x] diagnosticare il fallimento causato da `eth0` inesistente;
- [x] creare un backup della configurazione;
- [x] configurare `HOME_NET` con `10.42.0.0/24`;
- [x] configurare l'interfaccia hotspot reale;
- [x] installare e verificare le regole;
- [x] verificare la configurazione con codice di uscita `0`;
- [x] eseguire Suricata manualmente in modalità IDS;
- [x] generare traffico autorizzato;
- [x] leggere `fast.log`, `eve.json` e `suricata.log`;
- [x] osservare DNS, HTTP, TLS, QUIC, mDNS, DHCP, flow e fileinfo;
- [x] registrare un alert reale;
- [x] controllare errori e pacchetti persi;
- [x] verificare l'arresto controllato senza interrompere routing e hotspot.

## Attività ancora da completare

- [ ] provare `systemctl start suricata` con servizio disabilitato al boot;
- [ ] verificare la combinazione `active` e `disabled`;
- [ ] provare `systemctl stop suricata` e controllare la chiusura;
- [ ] creare una regola locale innocua per un alert intenzionale e ripetibile;
- [ ] verificare la frequenza globale di logrotate;
- [ ] decidere la conservazione finale dei log;
- [ ] misurare i drop durante una prova più lunga;
- [ ] documentare eventuali falsi positivi e tuning;
- [ ] creare estratti pubblici anonimizzati e report privato completo.

## Comandi principali verificati

```bash
suricata -V
suricata --build-info
suricata-update --version
jq --version
sudo suricata -T -c /etc/suricata/suricata.yaml
sudo jq -r '.event_type' /var/log/suricata/eve.json | sort | uniq -c | sort -nr
sudo tail -n 30 /var/log/suricata/fast.log
sudo tail -n 40 /var/log/suricata/suricata.log
```

## Privacy

Non pubblicare:

- nome completo dell'interfaccia USB se incorpora il MAC;
- indirizzi MAC;
- frame Ethernet grezzi;
- IP e porte completi non necessari;
- query DNS personali;
- log integrali;
- hostname e percorsi locali;
- file `eve.json` o PCAP grezzi.

## Rollback

Arrestare Suricata:

```bash
sudo systemctl stop suricata
```

Assicurarsi che non parta automaticamente:

```bash
sudo systemctl disable suricata
```

Ripristino della configurazione:

```bash
sudo cp -a \
    /etc/suricata/suricata.yaml.backup-<TIMESTAMP> \
    /etc/suricata/suricata.yaml
```

Verifica dopo il ripristino:

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml
```

## Condizione di completamento

La fase sarà completata quando:

- l'avvio e l'arresto su richiesta tramite systemd saranno verificati;
- sarà prodotto un alert di test innocuo e ripetibile;
- la rotazione e conservazione dei log saranno definite;
- una prova più lunga confermerà drop non anomali;
- report pubblico e privato saranno aggiornati.

## Prossimo passo

Alla ripresa, eseguire la prova di avvio su richiesta tramite systemd mantenendo Suricata disabilitato al boot:

```bash
sudo systemctl daemon-reload
sudo systemctl disable suricata
sudo systemctl start suricata
systemctl is-active suricata
systemctl is-enabled suricata
```

Risultato atteso durante la prova:

```text
active
disabled
```

Poi arrestare con:

```bash
sudo systemctl stop suricata
```
