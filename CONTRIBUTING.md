# Contributing

Contributi, correzioni e miglioramenti sono benvenuti, purché mantengano il progetto sicuro, riproducibile e comprensibile.

## Principi

- spiegare la teoria, non soltanto fornire comandi;
- commentare script e configurazioni;
- evitare privilegi non necessari;
- non includere dati sensibili;
- indicare chiaramente quali passaggi modificano la rete;
- fornire sempre una procedura di verifica e rollback;
- distinguere comandi eseguiti da comandi proposti;
- usare ambienti propri o autorizzati.

## Prima di proporre una modifica

1. verificare che non siano presenti password, token, MAC reali o dati personali;
2. testare in una macchina virtuale o rete isolata;
3. aggiornare la documentazione;
4. descrivere il comportamento atteso;
5. indicare distribuzione e versione usate;
6. aggiungere una procedura di rollback per modifiche a firewall o routing.

## Stile degli script

Gli script shell devono preferibilmente usare:

```bash
#!/usr/bin/env bash
set -u
set -o pipefail
```

Usare `set -e` solo quando il comportamento di uscita immediata è stato valutato attentamente.

Gli script devono:

- validare gli argomenti;
- usare nomi di variabile descrittivi;
- citare le variabili;
- mostrare messaggi di errore comprensibili;
- evitare modifiche distruttive implicite;
- supportare una modalità di verifica quando possibile.

## Configurazioni di rete

Non assumere che tutte le macchine usino `eth0` ed `eth1`. Documentare sempre le variabili:

```text
WAN_IFACE
LAN_IFACE
LAN_SUBNET
GATEWAY_IP
CLIENT_IP
```

Le configurazioni di esempio possono usare:

```text
WAN_IFACE=eth0
LAN_IFACE=eth1
LAN_SUBNET=10.10.10.0/24
GATEWAY_IP=10.10.10.2
CLIENT_IP=10.10.10.3
```

## Commit

Messaggi consigliati:

```text
docs: explain connection tracking
feat: add network state collector
fix: restrict masquerade to LAN subnet
refactor: split firewall and NAT tables
```

## Pull request

La descrizione dovrebbe includere:

- problema risolto;
- modifica effettuata;
- ambiente di test;
- comandi di verifica;
- rischi;
- rollback;
- eventuali screenshot anonimizzati.

## Documentazione

La documentazione principale è in italiano. Termini tecnici inglesi possono essere mantenuti quando sono quelli usati dagli strumenti Linux, ma vanno spiegati alla prima occorrenza.

## Condotta responsabile

Non proporre funzionalità orientate all'accesso non autorizzato, all'intercettazione di terzi o all'occultamento di attività illecite. Il progetto è finalizzato a sicurezza difensiva, amministrazione e apprendimento.