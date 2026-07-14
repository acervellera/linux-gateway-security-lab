# Fase 10 — Database e dashboard con Docker

## Stato

```text
DA FARE
```

## Obiettivo

Containerizzare i servizi applicativi che archiviano e mostrano le statistiche prodotte da Python, senza affidare a Docker il routing principale del gateway.

## Separazione delle responsabilità

```text
Ubuntu host
    hotspot, DHCP, routing, firewall, Suricata e Zeek

Docker
    importazione dati, database, API e dashboard
```

## Principi di sicurezza

- evitare `privileged: true`;
- evitare `network_mode: host` salvo necessità verificata;
- non montare `/var/run/docker.sock`;
- montare i log in sola lettura;
- usare utenti non root nei container quando possibile;
- limitare porte pubblicate;
- usare volumi dedicati;
- conservare segreti fuori dal repository;
- applicare healthcheck e limiti di risorse.

## Possibile architettura

```text
Log Suricata / Zeek
        |
        v
Importer Python
        |
        v
Database
        |
        +--> API o query
        |
        v
Dashboard
```

## Componenti da scegliere

La scelta sarà fatta dopo aver misurato quantità e formato dei dati. Possibili componenti:

- PostgreSQL per dati strutturati;
- SQLite per una prima versione semplice;
- Grafana per visualizzazione;
- una piccola API Python;
- una dashboard Python dedicata.

Non installeremo più componenti del necessario.

## Struttura prevista

```text
docker/
|-- compose.yaml
|-- .env.example
|-- importer/
|-- dashboard/
`-- database/
```

Il file `.env` reale resterà escluso da Git.

## Dati da mostrare

- connessioni nel tempo;
- dispositivi osservati;
- IP più contattati;
- domini DNS più richiesti;
- porte e protocolli;
- byte inviati e ricevuti;
- alert Suricata;
- eventi importanti Zeek;
- stato dell'importazione;
- dimensione e ritardo dei log.

## Attività previste

- [ ] definire schema dati;
- [ ] creare importazione idempotente;
- [ ] gestire record duplicati;
- [ ] creare volumi;
- [ ] creare rete Docker separata;
- [ ] configurare healthcheck;
- [ ] avviare lo stack;
- [ ] importare un campione;
- [ ] confrontare dashboard e report Python;
- [ ] testare arresto, riavvio e backup.

## Verifiche

```bash
docker compose config
docker compose up -d
docker compose ps
docker compose logs
```

Ogni comando e opzione verrà spiegato nel documento quando lo stack reale sarà stato scelto.

## Condizione di completamento

- i dati Python entrano nel database;
- la dashboard mostra valori verificabili;
- i container non controllano il firewall host;
- i log sono montati in sola lettura;
- lo stack riparte senza perdita inattesa;
- backup e ripristino del database sono documentati.

## Rollback

```bash
docker compose down
```

La rimozione dei volumi sarà un'azione separata e mai implicita.

## Prossimo passo

Eseguire collaudo completo, hardening, backup e ripristino.