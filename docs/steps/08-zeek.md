# Fase 8 — Zeek e log di rete

## Stato

```text
COMPLETATA E VERIFICATA — 21 luglio 2026
```

Zeek è stato installato sul gateway Ubuntu, configurato come sensore standalone e verificato sia con una cattura manuale sia tramite ZeekControl.

La modalità operativa scelta è manuale: Zeek viene avviato soltanto durante le sessioni di laboratorio e resta fermo durante il normale funzionamento del gateway.

## Obiettivo raggiunto

Il gateway osserva passivamente il traffico della rete autorizzata `10.42.0.0/24` e produce log JSON strutturati relativi a connessioni, DNS, TLS e QUIC.

Zeek:

```text
osserva -> interpreta protocolli -> registra metadati
```

Non sostituisce il firewall e non blocca il traffico.

## Collocazione architetturale

Zeek è installato direttamente sull'host Ubuntu, come Suricata.

```text
Ubuntu host
    hotspot, DHCP, routing, firewall, Suricata e Zeek

Docker
    importazione dati, database, API e dashboard
```

La cattura avviene sull'interfaccia fisica dell'hotspot, prima del NAT, così nei log compare l'indirizzo reale del client della rete di laboratorio.

## Ambiente anonimizzato

```text
Sistema:       Ubuntu 26.04 LTS
Architettura:  amd64
LAB_SUBNET:    10.42.0.0/24
GATEWAY_IP:    10.42.0.1
AP_IF:         wlx<REDACTED>
UPLINK_IF:     wlp13s0
Orologio:      sincronizzato tramite NTP
Spazio libero: circa 739 GiB
```

Il nome completo dell'interfaccia USB contiene un indirizzo MAC e non viene pubblicato.

## Installazione

I repository Ubuntu configurati non contenevano un pacchetto Zeek candidato. È stato quindi aggiunto il repository ufficiale per Ubuntu 26.04 con una chiave dedicata tramite `signed-by`.

Pacchetti verificati:

```text
Zeek:         8.0.9
ZeekControl:  2.6.0-31
Prefisso:     /opt/zeek
```

Eseguibili principali:

```text
/opt/zeek/bin/zeek
/opt/zeek/bin/zeekctl
/opt/zeek/bin/zkg
```

Non è stata installata un'unità systemd Zeek. La gestione avviene tramite ZeekControl.

## Funzionalità verificate

Il comando:

```bash
/opt/zeek/bin/zeek -N
```

ha confermato, tra gli altri, i componenti:

```text
Zeek::AF_Packet
Zeek::Pcap
Zeek::DNS
Zeek::HTTP
Zeek::SSL
Zeek::QUIC
Zeek::X509
```

## Prima cattura manuale

Prima di configurare ZeekControl è stata eseguita una cattura diretta in una directory privata:

```bash
sudo /opt/zeek/bin/zeek \
    -C \
    -i "$AP_IF" \
    -e 'Site::local_nets += { 10.42.0.0/24 };' \
    local \
    policy/tuning/json-logs
```

Significato essenziale:

- `-C`: ignora checksum apparentemente errati dovuti all'offloading;
- `-i`: seleziona l'interfaccia di cattura;
- `Site::local_nets`: definisce la subnet del laboratorio;
- `local`: carica la configurazione locale standard;
- `json-logs`: produce un oggetto JSON per riga.

Riepilogo osservato:

```text
pacchetti ricevuti:       12850
pacchetti kernel persi:   0
pacchetti non elaborati:  4, pari allo 0,03%
gap TCP stimati:          0
perdita TCP stimata:      0,0%
connessioni con gap:      0
byte mancanti:            0
```

`reporter.log` conteneva soltanto messaggi informativi relativi al segnale di arresto e al riepilogo della cattura.

## Log della cattura manuale

Sono stati creati log JSON validi, tra cui:

```text
capture_loss.log
conn.log
dns.log
known_hosts.log
known_services.log
loaded_scripts.log
packet_filter.log
quic.log
reporter.log
ssl.log
stats.log
telemetry.log
```

Eventi principali osservati:

```text
conn.log    56
 dns.log     67
ssl.log     32
quic.log    20
```

L'assenza di `http.log` durante questa prova è coerente con traffico web quasi interamente cifrato. `x509.log`, `notice.log` e `weird.log` non sono obbligatori e vengono creati soltanto quando Zeek osserva eventi pertinenti.

## Configurazione ZeekControl

Prima delle modifiche è stato creato un backup privato dei file:

```text
/opt/zeek/etc/node.cfg
/opt/zeek/etc/networks.cfg
/opt/zeek/etc/zeekctl.cfg
/opt/zeek/share/zeek/site/local.zeek
```

### Nodo standalone

`node.cfg` usa un solo nodo:

```ini
[zeek]
type=standalone
host=localhost
interface=wlx<REDACTED>
```

### Rete locale

`networks.cfg` contiene soltanto la rete autorizzata:

```text
10.42.0.0/24    Rete laboratorio autorizzata
```

In `zeekctl.cfg` è stato aggiunto:

```ini
PrivateAddressSpaceIsLocal = 0
```

In questo modo ZeekControl non considera automaticamente locale tutto lo spazio RFC 1918; la classificazione locale dipende dalle reti indicate esplicitamente in `networks.cfg`.

### Configurazione locale

In `local.zeek`:

- il valore predefinito di `digest_salt` è stato sostituito con un valore casuale;
- è stato abilitato il formato JSON.

```zeek
@load policy/tuning/json-logs
```

Il valore reale del salt non viene documentato né pubblicato.

## Controllo della configurazione

Prima del deploy è stato eseguito:

```bash
sudo /opt/zeek/bin/zeekctl check
```

Risultato:

```text
zeek scripts are ok.
```

## Avvio gestito

Per isolare il test, Suricata è stato fermato temporaneamente e Zeek è stato avviato tramite ZeekControl:

```bash
sudo systemctl stop suricata
sudo /opt/zeek/bin/zeekctl deploy
sudo /opt/zeek/bin/zeekctl status
```

Stato verificato durante l'esecuzione:

```text
Name  Type        Host       Status
zeek  standalone  localhost  running
```

Dopo aver generato traffico autorizzato, i log principali contenevano:

```text
conn.log    19 eventi
 dns.log     85 eventi
ssl.log     13 eventi
quic.log    13 eventi
```

Tutti i file controllati erano JSON validi.

## Rotazione e archiviazione

La configurazione installata usa:

```ini
LogRotationInterval = 3600
LogExpireInterval = 0
```

L'intervallo configurato è quindi di un'ora e la cancellazione automatica è disabilitata.

All'arresto gestito, i log non sono rimasti in `logs/current`: sono stati archiviati sotto `/opt/zeek/logs` e risultavano leggibili anche quando compressi come `.log.gz`.

La rotazione oraria completa non è stata attesa per un'ora; è stata verificata l'archiviazione gestita all'arresto e la relativa leggibilità.

## Arresto e ripristino

Comandi verificati:

```bash
sudo /opt/zeek/bin/zeekctl stop
sudo systemctl start suricata
```

Stato finale:

```text
Zeek:      stopped
Suricata:  active
```

L'arresto di Zeek non ha interrotto hotspot, routing, NAT o accesso Internet.

## Modalità operativa scelta

```text
normalmente:            Zeek spento
sessione di laboratorio: avvio manuale con zeekctl deploy
fine laboratorio:       arresto con zeekctl stop
avvio al boot:          non configurato
```

Questa scelta riduce il consumo di risorse e mantiene separati i test di Zeek e Suricata.

## Lettura dei log protetti

Una redirezione come:

```bash
sudo wc -l < file.log
```

può fallire perché la shell tenta di aprire il file prima di eseguire `sudo`.

Forme corrette:

```bash
sudo wc -l file.log
sudo cat file.log | wc -l
sudo gzip -cd file.log.gz | wc -l
```

## Test di completamento

- [x] Zeek installato e versione registrata;
- [x] plugin di cattura disponibili;
- [x] interfaccia hotspot configurata;
- [x] rete `10.42.0.0/24` definita come locale;
- [x] test manuale completato;
- [x] cattura senza pacchetti persi dal kernel;
- [x] nessun gap TCP o byte mancante osservato;
- [x] richiesta DNS presente in `dns.log`;
- [x] connessione HTTPS presente in `conn.log` e `ssl.log`;
- [x] traffico QUIC presente in `quic.log`;
- [x] indirizzo del client corretto e precedente al NAT;
- [x] byte e durata plausibili;
- [x] formato JSON verificato con `jq`;
- [x] avvio e arresto gestiti con ZeekControl;
- [x] archiviazione dei log all'arresto verificata;
- [x] arresto di Zeek senza interruzione del gateway;
- [x] Suricata ripristinato e attivo;
- [ ] rotazione oraria osservata per un intervallo completo;
- [ ] primo programma Python dedicato ai log Zeek.

## Privacy

Non pubblicare:

- nome completo dell'interfaccia USB;
- indirizzi MAC;
- IP completi dei client;
- domini e query DNS personali;
- URI HTTP;
- server name TLS;
- certificati e log grezzi;
- valore di `digest_salt`;
- backup locali della configurazione.

I log di prova e i backup restano fuori dal repository.

## Rollback

Per fermare Zeek:

```bash
sudo /opt/zeek/bin/zeekctl stop
```

Per ripristinare la configurazione, copiare i file dal backup privato creato prima delle modifiche e rieseguire:

```bash
sudo /opt/zeek/bin/zeekctl check
```

Rimuovere soltanto i log di test non più necessari. Zeek non modifica routing, NAT o firewall.

## Prossimo passo

Fase 9: scrivere il primo programma Python che legge i log JSON di Zeek senza modificare la rete.