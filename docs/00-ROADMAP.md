# Roadmap completa

## Obiettivo generale

Costruire un gateway Ubuntu attraverso cui far passare il traffico di dispositivi di laboratorio, osservarlo in modo difensivo e analizzarne i log con Python.

## Architettura finale

```text
Client autorizzato
      |
      v
Hotspot Realtek USB
      |
      v
Ubuntu gateway
      |-- DHCP / DNS locale
      |-- routing e NAT
      |-- nftables
      |-- tcpdump
      |-- Suricata
      |-- Zeek
      |-- Python
      `-- Docker
      |
      v
MediaTek interna
      |
      v
Internet
```

## Sequenza delle fasi

| Fase | Documento | Risultato richiesto | Stato attuale |
|---:|---|---|---|
| 1 | [`steps/01-inventario-hardware-rete.md`](steps/01-inventario-hardware-rete.md) | Identificare hardware, driver, interfacce e uplink | COMPLETATO |
| 2 | [`steps/02-topologia-e-indirizzamento.md`](steps/02-topologia-e-indirizzamento.md) | Definire nomi, subnet, gateway e percorso dei pacchetti | COMPLETATO |
| 3 | [`steps/03-hotspot-realtek.md`](steps/03-hotspot-realtek.md) | Creare un hotspot stabile sulla Realtek USB | COMPLETATO |
| 4 | [`steps/04-dhcp-routing-nat.md`](steps/04-dhcp-routing-nat.md) | Verificare e documentare la navigazione del client attraverso Ubuntu | PROSSIMO |
| 5 | [`steps/05-firewall-nftables.md`](steps/05-firewall-nftables.md) | Applicare regole stateful e un rollback sicuro | DA FARE |
| 6 | [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md) | Osservare DNS, TCP, TLS e traffico inoltrato | DA FARE |
| 7 | [`steps/07-suricata.md`](steps/07-suricata.md) | Produrre e verificare avvisi IDS | DA FARE |
| 8 | [`steps/08-zeek.md`](steps/08-zeek.md) | Generare log `conn`, `dns`, `http`, `ssl` e `notice` | DA FARE |
| 9 | [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md) | Leggere i log e produrre statistiche e report | DA FARE |
| 10 | [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md) | Salvare e visualizzare i dati tramite container | DA FARE |
| 11 | [`steps/11-test-hardening-backup.md`](steps/11-test-hardening-backup.md) | Eseguire test finali, hardening, backup e ripristino | DA FARE |

## Fase 1 — Inventario

Sono stati verificati:

- versione di Ubuntu e kernel;
- nomi reali delle interfacce;
- modello e driver della MediaTek interna;
- modello e driver della Realtek USB;
- supporto dichiarato della modalità Access Point;
- interfaccia realmente usata per Internet;
- gestione delle schede da parte di NetworkManager;
- assenza di blocchi `rfkill`;
- servizi e reti virtuali già presenti.

Nessuna configurazione è stata modificata in questa fase.

## Fase 2 — Topologia e piano IP

La fase 2 è stata completata e verificata il 15 luglio 2026.

Sono stati definiti:

- `UPLINK_IF`: MediaTek `wlp13s0` verso Internet;
- `AP_IF`: Realtek USB, anonimizzata come `wlx<REDACTED>` nel repository;
- subnet del laboratorio;
- indirizzo del gateway Ubuntu;
- intervallo e durata DHCP;
- DNS distribuito ai client;
- nome del profilo NetworkManager;
- SSID non personale;
- banda e canale iniziali;
- comportamento IPv6 iniziale;
- politica di isolamento dei client;
- percorso previsto dei pacchetti;
- convivenza con Docker, libvirt e rete domestica.

Piano verificato:

```text
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
DHCP_RANGE=10.42.0.50-10.42.0.200
DHCP_LEASE_SECONDS=3600
DNS_SERVER=10.42.0.1
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
IPV6_MODE=disabled-on-hotspot-initially
CLIENT_ISOLATION=enable-if-supported
```

La subnet `10.42.0.0/24` non si sovrappone alle reti osservate:

```text
192.168.10.0/24
192.168.122.0/24
10.10.10.0/24
172.17.0.0/16
172.18.0.0/16
```

Il dominio regolamentare osservato durante la pianificazione era `GB`. La correzione è stata affrontata nella fase 3.

Nessuna configurazione di rete è stata modificata durante la fase 2.

## Fase 3 — Hotspot Realtek

La fase 3 è stata completata e verificata il 15 luglio 2026.

Sono stati completati:

- richiesta del dominio regolamentare italiano, con risultato effettivo `country 98: DFS-ETSI`;
- creazione del profilo `security-gateway-ap` sulla sola Realtek USB;
- configurazione di `SecurityGatewayLab` in modalità `AP`;
- banda 2,4 GHz e canale 6;
- sicurezza WPA-PSK con segreto non pubblicato;
- indirizzo gateway `10.42.0.1/24`;
- condivisione IPv4 tramite `ipv4.method shared`;
- disabilitazione IPv6 sul solo profilo hotspot iniziale;
- disabilitazione dell'avvio automatico con `connection.autoconnect=no`;
- associazione contemporanea di client reali;
- assegnazione di un indirizzo `10.42.0.x`;
- raggiungibilità del gateway dal client tramite richiesta HTTP con risposta `200`;
- mantenimento dell'uplink Internet sulla MediaTek `wlp13s0`;
- salvataggio locale dello stato completo di NetworkManager con segreti nascosti;
- arresto e riattivazione dell'hotspot;
- eliminazione completa del profilo;
- verifica della rimozione di `10.42.0.1/24` dalla Realtek;
- ricreazione e riattivazione del profilo con gli stessi parametri.

È stata anche osservata navigazione Internet dal telefono attraverso la connessione condivisa. La spiegazione dettagliata di DHCP, DNS, forwarding e NAT resta assegnata alla fase 4.

Il test dopo riavvio è rinviato alla fase 11, insieme alla verifica della persistenza e dell'hardening finale.

## Fase 4 — DHCP, routing e NAT

NetworkManager ha già dimostrato empiricamente che la modalità `shared` permette al client di navigare. In questa fase il comportamento verrà separato, osservato e documentato.

Ordine di lavoro:

1. verificare indirizzo, gateway e DNS ricevuti dal client;
2. identificare il servizio DHCP e DNS forwarding gestito da NetworkManager;
3. controllare lo stato del forwarding IPv4;
4. identificare le regole NAT/masquerading create automaticamente;
5. verificare il percorso client → gateway;
6. testare separatamente raggiungibilità di un IP esterno;
7. testare la risoluzione DNS;
8. documentare conntrack e traduzione NAT inversa;
9. rendere persistente solo ciò che ha funzionato.

## Fase 5 — Firewall nftables

Costruiremo un firewall stateful con:

- policy chiare;
- protezione del gateway;
- inoltro LAN → WAN controllato;
- ritorno `established,related`;
- NAT limitato alla subnet del laboratorio;
- logging con rate limit;
- salvataggio del ruleset precedente;
- rollback automatico o console locale disponibile.

## Fase 6 — tcpdump

Impareremo a:

- scegliere l'interfaccia corretta;
- filtrare per host, porta e protocollo;
- distinguere lato hotspot e lato uplink;
- osservare una richiesta DNS;
- osservare handshake TCP e TLS;
- salvare catture limitate e anonimizzate;
- evitare di pubblicare traffico sensibile.

## Fase 7 — Suricata

Passi previsti:

- installazione;
- scelta dell'interfaccia;
- aggiornamento regole;
- verifica della configurazione;
- avvio controllato;
- generazione di traffico di test autorizzato;
- lettura di `fast.log`, `eve.json` e statistiche;
- riduzione dei falsi positivi.

## Fase 8 — Zeek

Passi previsti:

- installazione;
- configurazione dell'interfaccia;
- esecuzione iniziale;
- analisi di `conn.log`, `dns.log`, `http.log`, `ssl.log` e `notice.log`;
- comprensione del formato TSV o JSON;
- rotazione e conservazione dei log.

## Fase 9 — Python

Il percorso Python sarà progressivo:

1. aprire e leggere un file;
2. gestire righe e colonne;
3. usare dizionari e contatori;
4. leggere JSON di Suricata;
5. leggere log Zeek;
6. calcolare IP, domini e porte più frequenti;
7. raggruppare per dispositivo e ora;
8. esportare CSV e JSON;
9. aggiungere error handling e logging;
10. creare test automatici.

Ogni libreria e ogni parte del codice verranno commentate e spiegate.

## Fase 10 — Docker

Docker verrà aggiunto dopo che la pipeline locale sarà stabile.

Possibile stack:

- applicazione Python di importazione;
- PostgreSQL o altro database scelto;
- Grafana o dashboard web;
- volumi dedicati;
- rete Docker separata;
- accesso ai log in sola lettura;
- nessun container privilegiato senza necessità dimostrata.

## Fase 11 — Test e hardening

Verificheremo:

- riavvio del gateway;
- persistenza delle configurazioni;
- comportamento con `connection.autoconnect=no` e successiva politica definitiva;
- isolamento e accessi consentiti tra client e reti;
- comportamento con uplink assente;
- comportamento con IDS fermo;
- spazio occupato dai log;
- rotazione;
- backup delle configurazioni;
- procedura di ripristino;
- rimozione sicura dell'intero laboratorio.

## Criterio di completamento del progetto

Il progetto è completato quando un dispositivo autorizzato:

1. si collega all'hotspot Realtek;
2. riceve una configurazione IP corretta;
3. usa Ubuntu come unico gateway;
4. raggiunge Internet tramite MediaTek;
5. è filtrato da `nftables`;
6. genera log leggibili da Suricata e Zeek;
7. compare nei report Python;
8. compare nella dashboard Docker;
9. continua a funzionare dopo un riavvio controllato;
10. può essere disconnesso e ripristinato con procedure documentate.