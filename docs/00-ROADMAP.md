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
| 4 | [`steps/04-dhcp-routing-nat.md`](steps/04-dhcp-routing-nat.md) | Verificare DHCP, DNS, forwarding, NAT e sicurezza Wi-Fi | COMPLETATO |
| 5 | [`steps/05-firewall-nftables.md`](steps/05-firewall-nftables.md) | Applicare regole stateful e un rollback sicuro | PROSSIMO |
| 6 | [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md) | Approfondire cattura, filtri e salvataggio revisionato | DA FARE |
| 7 | [`steps/07-suricata.md`](steps/07-suricata.md) | Produrre e verificare avvisi IDS | DA FARE |
| 8 | [`steps/08-zeek.md`](steps/08-zeek.md) | Generare log `conn`, `dns`, `http`, `ssl` e `notice` | DA FARE |
| 9 | [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md) | Leggere i log e produrre statistiche e report | DA FARE |
| 10 | [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md) | Salvare e visualizzare i dati tramite container | DA FARE |
| 11 | [`steps/11-test-hardening-backup.md`](steps/11-test-hardening-backup.md) | Eseguire test finali, hardening, backup e ripristino | DA FARE |

## Fase 1 — Inventario

Sono stati verificati:

- versione di Ubuntu e kernel;
- nomi reali delle interfacce;
- MediaTek interna e driver;
- Realtek USB e driver;
- supporto modalità Access Point;
- interfaccia realmente usata per Internet;
- gestione NetworkManager;
- assenza di blocchi `rfkill`;
- servizi e reti virtuali già presenti.

## Fase 2 — Topologia e piano IP

Piano verificato:

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
DNS_SERVER=10.42.0.1
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
```

La rete `10.42.0.0/24` non si sovrappone alle reti dell'uplink, libvirt o Docker osservate.

## Fase 3 — Hotspot Realtek

Completata e verificata il 15 luglio 2026.

Risultati principali:

- profilo `security-gateway-ap`;
- modalità AP sulla Realtek;
- `10.42.0.1/24`;
- `ipv4.method=shared`;
- client reali associati;
- gateway raggiunto;
- route predefinita mantenuta sulla MediaTek;
- rollback del profilo verificato.

## Fase 4 — DHCP, routing e NAT

Completata e verificata il 16 luglio 2026.

Sono stati verificati:

- `dnsmasq` per DHCP e DNS;
- sequenza DHCP completa;
- `net.ipv4.ip_forward=1`;
- regole automatiche di forwarding;
- regola di masquerading per `10.42.0.0/24`;
- contatori NAT non nulli;
- traffico prima del NAT sulla Realtek;
- traffico dopo il NAT sulla MediaTek;
- risoluzione DNS classica;
- traffico TCP 443 e UDP 443;
- assenza di percorso cellulare alternativo durante il test;
- sicurezza Wi-Fi WPA2-RSN con CCMP/AES;
- eliminazione dell'avviso iOS relativo a TKIP.

Percorso dimostrato:

```text
client 10.42.0.x
  -> Realtek 10.42.0.1
  -> forwarding
  -> NAT/masquerading
  -> MediaTek 192.168.10.x
  -> router 192.168.10.1
  -> Internet
```

Il NAT traduce indirizzi e, se necessario, porte. Non cifra il traffico.

La cifratura viene fornita da:

- WPA2-RSN/CCMP sul collegamento radio;
- TLS/HTTPS/QUIC sul collegamento applicativo verso il server.

## Fase 5 — Firewall nftables

Prossima fase.

Obiettivi:

- salvare lo stato firewall corrente;
- distinguere regole automatiche di NetworkManager, Docker e libvirt;
- creare catene e policy stateful;
- consentire `established,related`;
- limitare il forwarding dalla subnet hotspot all'uplink;
- impedire accessi non previsti alla rete domestica;
- proteggere il gateway;
- aggiungere logging con rate limit;
- predisporre rollback sicuro;
- verificare DHCP, DNS e Internet dopo ogni modifica.

Non verrà usato un `flush ruleset` indiscriminato.

## Fase 6 — tcpdump

La fase 4 ha già usato `tcpdump` per dimostrare il NAT.

La fase 6 approfondirà:

- scelta dell'interfaccia;
- filtri BPF;
- DNS, TCP, TLS e QUIC;
- salvataggio `.pcap` limitato;
- anonimizzazione;
- confronto temporale tra lati hotspot e uplink;
- rischi di privacy.

## Fase 7 — Suricata

Passi previsti:

- installazione;
- scelta dell'interfaccia;
- aggiornamento regole;
- verifica della configurazione;
- traffico di test autorizzato;
- lettura di `fast.log`, `eve.json` e statistiche;
- riduzione dei falsi positivi.

## Fase 8 — Zeek

Passi previsti:

- installazione;
- configurazione;
- analisi di `conn.log`, `dns.log`, `http.log`, `ssl.log` e `notice.log`;
- formato TSV o JSON;
- rotazione e conservazione.

## Fase 9 — Python

Percorso progressivo:

1. leggere file;
2. gestire righe e colonne;
3. usare funzioni, dizionari e contatori;
4. leggere JSON Suricata;
5. leggere log Zeek;
6. calcolare IP, domini e porte frequenti;
7. raggruppare per dispositivo e tempo;
8. esportare CSV e JSON;
9. aggiungere error handling e logging;
10. creare test.

Ogni libreria e ogni parte del codice verranno commentate.

## Fase 10 — Docker

Docker verrà usato per servizi applicativi:

- importazione;
- database;
- dashboard;
- volumi;
- rete separata;
- accesso ai log in sola lettura.

Nessun container privilegiato senza necessità dimostrata.

## Fase 11 — Test e hardening

Verifiche finali:

- riavvio;
- persistenza;
- uplink assente;
- isolamento tra client;
- accessi consentiti tra reti;
- IDS fermo;
- spazio e rotazione log;
- backup;
- ripristino;
- rimozione sicura del laboratorio.

## Criterio di completamento del progetto

Il progetto è completato quando un dispositivo autorizzato:

1. si collega all'hotspot;
2. riceve configurazione IP corretta;
3. usa Ubuntu come unico gateway;
4. raggiunge Internet tramite MediaTek;
5. è filtrato da `nftables`;
6. genera log Suricata e Zeek;
7. compare nei report Python;
8. compare nella dashboard Docker;
9. continua a funzionare dopo test controllati;
10. può essere disconnesso e ripristinato con procedure documentate.
