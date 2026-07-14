# Fase 7 — Suricata IDS

## Stato

```text
DA FARE
```

## Obiettivo

Installare Suricata sul gateway, osservare il traffico del laboratorio e produrre avvisi e log JSON utilizzabili da Python.

## Ruolo di Suricata

Suricata è un motore IDS/IPS e di monitoraggio di rete. In questo progetto verrà introdotto inizialmente in modalità passiva IDS: osserva e segnala, senza bloccare automaticamente il traffico.

## Prerequisiti

- routing e firewall stabili;
- traffico visibile con `tcpdump`;
- interfaccia di osservazione scelta;
- spazio disco disponibile;
- orologio di sistema corretto;
- politica di conservazione dei log.

## Attività previste

- [ ] installare il pacchetto;
- [ ] registrare versione e build info;
- [ ] scegliere modalità di cattura;
- [ ] configurare `HOME_NET` con la subnet del laboratorio;
- [ ] verificare la configurazione;
- [ ] aggiornare le regole;
- [ ] avviare il servizio;
- [ ] controllare statistiche ed errori;
- [ ] generare traffico di test autorizzato;
- [ ] leggere `fast.log` ed `eve.json`;
- [ ] documentare falsi positivi e tuning.

## Controlli previsti

```bash
suricata --build-info
sudo suricata -T -c /etc/suricata/suricata.yaml
systemctl status suricata
journalctl -u suricata
```

Le opzioni e i percorsi verranno verificati sulla versione realmente installata.

## Log principali

```text
fast.log       riepilogo testuale degli alert
eve.json       eventi JSON strutturati
stats.log      statistiche del motore
suricata.log   messaggi operativi
```

## Eventi da studiare

- alert;
- flow;
- dns;
- http;
- tls;
- fileinfo, quando presente;
- statistiche e pacchetti persi.

## Test sicuri

Useremo soltanto traffico generato nel laboratorio e regole di test innocue. Non verranno eseguite scansioni o prove contro sistemi esterni non autorizzati.

## Condizione di completamento

- Suricata parte senza errori di configurazione;
- osserva l'interfaccia scelta;
- produce `eve.json`;
- registra almeno un evento di test controllato;
- non perde una quantità anomala di pacchetti;
- i log sono ruotati e leggibili;
- il servizio può essere fermato senza interrompere il routing.

## Rollback

Fermare e disabilitare il servizio senza rimuovere configurazioni finché non sono stati raccolti i dati necessari:

```bash
sudo systemctl stop suricata
sudo systemctl disable suricata
```

La rimozione dei pacchetti verrà documentata solo se necessaria.

## File previsti

```text
configs/suricata/
samples/suricata/
```

Saranno aggiunti soltanto estratti anonimizzati e configurazioni verificate.

## Prossimo passo

Installare Zeek e confrontare i suoi log di rete con gli eventi Suricata.